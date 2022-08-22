from Orange.evaluation.testing import Results
import Orange.evaluation
import numpy
import logging
from typing import List, Optional
from Orange.data import Table
from Orange.widgets import gui
from Orange.widgets.settings import Setting
from Orange.widgets.widget import OWWidget, Input, Output, Msg

import concurrent.futures
from Orange.widgets.utils.concurrent import ThreadExecutor, FutureWatcher, methodinvoke
from Orange.widgets.utils.widgetpreview import WidgetPreview
from AnyQt.QtCore import QThread, pyqtSlot
from functools import reduce, partial

from orangecontrib.hxl.base import FileRAW
from orangecontrib.hxl.widgets.utils import hash_intentionaly_weak

from orangecontrib.hxl.base import DataVault

log = logging.getLogger(__name__)


class HXLDownloadFile(OWWidget):
    """HXLDownloadFile"""
    # Widget needs a name, or it is considered an abstract widget
    # and not shown in the menu.
    name = "Download Raw File"
    id = "orangecontrib.hxl.widgets.downloadfile"
    description = """
    Download remote resource into a local FileRAW
    """
    icon = "icons/mywidget.svg"
    priority = 50  # where in the widget order it will appear
    category = "Orange3-HXLvisualETL"
    keywords = ["widget", "data"]
    want_main_area = False
    resizing_enabled = False

    res_alias = Setting("")
    res_hash = Setting("")
    source_uri_main = Setting("")
    source_uri_alt = Setting("")
    source_uri_alt2 = Setting("")

    # active_fileraw = None

    # class Inputs:
    #     """Inputs"""
    #     # specify the name of the input and the type
    #     data = Input("Data", Table)

    class Outputs:
        """Outputs"""
        # if there are two or more outputs, default=True marks the default output
        # data = Output("Data", Table, default=True, auto_summary=False)
        # data = Output("FileRAW", FileRAW, default=True, auto_summary=False)
        data = Output("FileRAW", FileRAW)
        # fileraw = Output("FileRAW", FileRAW, default=True, auto_summary=False)
        fileraw = Output("FileRAW", FileRAW, default=True)

    # same class can be initiated for Error and Information messages
    class Warning(OWWidget.Warning):
        """Warning"""
        warning = Msg("My warning!")

    def __init__(self):
        super().__init__()
        self.data = None

        self.vault = DataVault()
        self.fileraw = FileRAW()

        self.res_alias_box = gui.lineEdit(
            self.controlArea, self, "res_alias", box="Friendly alias (optional)")

        self.main_uri_box = gui.lineEdit(
            self.controlArea, self, "source_uri_main", box="Remote URI of main source", callback=self.commit)

        self.alt_uri_box = gui.lineEdit(
            self.controlArea, self, "source_uri_alt", box="Remote URI, backup alternative 1", callback=self.commit)

        self.alt2_uri_box = gui.lineEdit(
            self.controlArea, self, "source_uri_alt2", box="Remote URI, backup alternative 2", callback=self.commit)

        gui.separator(self.controlArea)
        self.optionsBox = gui.widgetBox(self.controlArea, "Options")

        gui.button(self.optionsBox, self, "(Re)Download", callback=self.commit)

        # self.res_hash_box.setText('teste')

        gui.separator(self.controlArea)
        box = gui.widgetBox(self.controlArea, "Info")
        self.infoa = gui.widgetLabel(box, "No comments")

        self.res_hash_box = gui.lineEdit(
            self.controlArea, self, "res_hash", box="Internal ID")
        self.res_hash_box.setDisabled(True)

        # log.exception('downloadfile init')

        # res_alias = self.res_alias_box.text()
        res_uri = self.main_uri_box.text()
        res_hash = str(hash_intentionaly_weak(res_uri))

        if DataVault.resource_summary('rawinput', res_hash) is not None:
            # log.exception('downloadfile init already exist, sending rigth now')
            self.commit()

        #: The current evaluating task (if any)
        self._task = None  # type: Optional[HXLDownloadFileTask]
        #: An executor we use to submit learner evaluations into a thread pool
        self._executor = ThreadExecutor()

    def _update(self):
        if self._task is not None:
            # First make sure any pending tasks are cancelled.
            self.cancel()
        assert self._task is None

        if self.data is None:
            return
        # collect all learners for which results have not yet been computed
        need_update = [
            (id, learner)
            for id, learner in self.learners.items()
            if self.results[id] is None
        ]
        if not need_update:
            return

        learners = [learner for _, learner in need_update]
        # setup the learner evaluations as partial function capturing
        # the necessary arguments.
        if self.testdata is None:
            learning_curve_func = partial(
                learning_curve,
                learners,
                self.data,
                folds=self.folds,
                proportions=self.curvePoints,
            )
        else:
            learning_curve_func = partial(
                learning_curve_with_test_data,
                learners,
                self.data,
                self.testdata,
                times=self.folds,
                proportions=self.curvePoints,
            )

        # setup the task state
        # self._task = task = Task()
        self._task = task = HXLDownloadFileTask()
        # The learning_curve[_with_test_data] also takes a callback function
        # to report the progress. We instrument this callback to both invoke
        # the appropriate slots on this widget for reporting the progress
        # (in a thread safe manner) and to implement cooperative cancellation.
        set_progress = methodinvoke(self, "setProgressValue", (float,))

        def callback(finished):
            # check if the task has been cancelled and raise an exception
            # from within. This 'strategy' can only be used with code that
            # properly cleans up after itself in the case of an exception
            # (does not leave any global locks, opened file descriptors, ...)
            if task.cancelled:
                raise KeyboardInterrupt()
            set_progress(finished * 100)

        # capture the callback in the partial function
        learning_curve_func = partial(learning_curve_func, callback=callback)

        self.progressBarInit()
        # Submit the evaluation function to the executor and fill in the
        # task with the resultant Future.
        task.future = self._executor.submit(learning_curve_func)
        # Setup the FutureWatcher to notify us of completion
        task.watcher = FutureWatcher(task.future)
        # by using FutureWatcher we ensure `_task_finished` slot will be
        # called from the main GUI thread by the Qt's event loop
        task.watcher.done.connect(self._task_finished)

    @pyqtSlot(float)
    def setProgressValue(self, value):
        assert self.thread() is QThread.currentThread()
        self.progressBarSet(value)

    @pyqtSlot(concurrent.futures.Future)
    def _task_finished(self, f):
        """
        Parameters
        ----------
        f : Future
            The future instance holding the result of learner evaluation.
        """
        assert self.thread() is QThread.currentThread()
        assert self._task is not None
        assert self._task.future is f
        assert f.done()

        self._task = None
        self.progressBarFinished()

        try:
            results = f.result()  # type: List[Results]
        except Exception as ex:
            # Log the exception with a traceback
            log = logging.getLogger()
            log.exception(__name__, exc_info=True)
            self.error("Exception occurred during evaluation: {!r}".format(ex))
            # clear all results
            for key in self.results.keys():
                self.results[key] = None
        else:
            # split the combined result into per learner/model results ...
            results = [
                list(Results.split_by_model(p_results)) for p_results in results
            ]  # type: List[List[Results]]
            assert all(len(r.learners) == 1 for r1 in results for r in r1)
            assert len(results) == len(self.curvePoints)

            learners = [r.learners[0] for r in results[0]]
            learner_id = {learner: id_ for id_,
                          learner in self.learners.items()}

            # ... and update self.results
            for i, learner in enumerate(learners):
                id_ = learner_id[learner]
                self.results[id_] = [p_results[i] for p_results in results]

    def onDeleteWidget(self):
        self.cancel()
        super().onDeleteWidget()

    # @Inputs.data
    # def set_data(self, data):
    #     """set_data"""
    #     if data:
    #         self.data = data
    #     else:
    #         self.data = None

    def commit(self):
        """commit"""
        # _hash_refs_a = self.res_id_box.text()
        # _hash_refs_b = self.main_uri_box.text()
        res_alias = self.res_alias_box.text()
        res_uri = self.main_uri_box.text()
        res_hash = str(hash_intentionaly_weak(res_uri))
        # if _hash_refs_a:
        #     res_hash = str(hash_intentionaly_weak(_hash_refs_a))
        #     self.infoa.setText(
        #         "_hash_refs_a " + res_hash)
        #     self.res_hash_box.setText(res_hash)
        # else:
        #     res_hash = str(hash_intentionaly_weak(_hash_refs_b))
        #     self.infoa.setText("_hash_refs_b " + res_hash)
        #     self.res_hash_box.setText(res_hash)

        result = self.vault.download_resource(res_uri, res_hash, res_alias)

        self.infoa.setText('result download_resource ' + str(result))

        self.fileraw.set_resource(res_hash, 'rawinput')

        # self.Outputs.data.send(self.data)
        # self.Outputs.data.send(self.fileraw)
        self.Outputs.fileraw.send(self.fileraw)

        # log.exception(
        #     f'downloadfile commit self.Outputs.fileraw [{str(self.fileraw)}] [{str(self.Outputs.fileraw)}]')
        # log.exception(
        #     f'downloadfile commit self.Outputs.data [{str(self.data)}] [{str(self.Outputs.data)}]')

    def handleNewSignals(self):
        self._update()

    def send_report(self):
        """send_report"""
        # self.report_plot() includes visualizations in the report
        self.report_caption(self.label)


class HXLDownloadFileTask:
    """
    A class that will hold the state for an learner evaluation.
    """

    #: A concurrent.futures.Future with our (eventual) results.
    #: The OWLearningCurveC class must fill this field
    future = ...  # type: concurrent.futures.Future

    #: FutureWatcher. Likewise this will be filled by OWLearningCurveC
    watcher = ...  # type: FutureWatcher

    #: True if this evaluation has been cancelled. The OWLearningCurveC
    #: will setup the task execution environment in such a way that this
    #: field will be checked periodically in the worker thread and cancel
    #: the computation if so required. In a sense this is the only
    #: communication channel in the direction from the OWLearningCurve to the
    #: worker thread
    cancelled = False  # type: bool

    def cancel(self):
        """
        Cancel the task.

        Set the `cancelled` field to True and block until the future is done.
        """
        # set cancelled state
        self.cancelled = True
        # cancel the future. Note this succeeds only if the execution has
        # not yet started (see `concurrent.futures.Future.cancel`) ..
        self.future.cancel()
        # ... and wait until computation finishes
        concurrent.futures.wait([self.future])


def learning_curve(
    learners, data, folds=10, proportions=None, random_state=None, callback=None
):

    if proportions is None:
        proportions = numpy.linspace(0.0, 1.0, 10 + 1, endpoint=True)[1:]

    def select_proportion_preproc(data, p, rstate=None):
        assert 0 < p <= 1
        rstate = numpy.random.RandomState(None) if rstate is None else rstate
        indices = rstate.permutation(len(data))
        n = int(numpy.ceil(len(data) * p))
        return data[indices[:n]]

    if callback is not None:
        parts_count = len(proportions)

        def callback_wrapped(part): return lambda value: callback(
            value / parts_count + part / parts_count
        )
    else:
        def callback_wrapped(part): return None

    results = [
        Orange.evaluation.CrossValidation(
            data,
            learners,
            k=folds,
            preprocessor=lambda data, p=p: select_proportion_preproc(data, p),
            callback=callback_wrapped(i),
        )
        for i, p in enumerate(proportions)
    ]
    return results


def learning_curve_with_test_data(
    learners,
    traindata,
    testdata,
    times=10,
    proportions=None,
    random_state=None,
    callback=None,
):
    if proportions is None:
        proportions = numpy.linspace(0.0, 1.0, 10 + 1, endpoint=True)[1:]

    def select_proportion_preproc(data, p, rstate=None):
        assert 0 < p <= 1
        rstate = numpy.random.RandomState(None) if rstate is None else rstate
        indices = rstate.permutation(len(data))
        n = int(numpy.ceil(len(data) * p))
        return data[indices[:n]]

    if callback is not None:
        parts_count = len(proportions) * times

        def callback_wrapped(part): return lambda value: callback(
            value / parts_count + part / parts_count
        )
    else:
        def callback_wrapped(part): return None

    results = [
        [
            Orange.evaluation.TestOnTestData(
                traindata,
                testdata,
                learners,
                preprocessor=lambda data, p=p: select_proportion_preproc(
                    data, p),
                callback=callback_wrapped(i * times + t),
            )
            for t in range(times)
        ]
        for i, p in enumerate(proportions)
    ]
    results = [reduce(results_add, res, Orange.evaluation.Results())
               for res in results]
    return results


def results_add(x, y):
    def is_empty(res):
        return (
            getattr(res, "models", None) is None
            and getattr(res, "row_indices", None) is None
        )

    if is_empty(x):
        return y
    elif is_empty(y):
        return x

    assert x.data is y.data
    assert x.domain is y.domain
    assert x.predicted.shape[0] == y.predicted.shape[0]

    assert len(x.learners) == len(y.learners)
    assert all(xl is yl for xl, yl in zip(x.learners, y.learners))

    row_indices = numpy.hstack((x.row_indices, y.row_indices))
    predicted = numpy.hstack((x.predicted, y.predicted))
    actual = numpy.hstack((x.actual, y.actual))

    xprob = getattr(x, "probabilities", None)
    yprob = getattr(y, "probabilities", None)

    if xprob is None and yprob is None:
        prob = None
    elif xprob is not None and yprob is not None:
        prob = numpy.concatenate((xprob, yprob), axis=1)
    else:
        raise ValueError()

    res = Orange.evaluation.Results()
    res.data = x.data
    res.domain = x.domain
    res.learners = x.learners
    res.row_indices = row_indices
    res.actual = actual
    res.predicted = predicted
    res.folds = None
    if prob is not None:
        res.probabilities = prob

    if x.models is not None and y.models is not None:
        res.models = [xm + ym for xm, ym in zip(x.models, y.models)]

    nmodels = predicted.shape[0]
    xfailed = getattr(x, "failed", None) or [False] * nmodels
    yfailed = getattr(y, "failed", None) or [False] * nmodels
    assert len(xfailed) == len(yfailed)
    res.failed = [xe or ye for xe, ye in zip(xfailed, yfailed)]

    return res


if __name__ == "__main__":
    from Orange.widgets.utils.widgetpreview import WidgetPreview  # since Orange 3.20.0
    WidgetPreview(HXLDownloadFile).run()
