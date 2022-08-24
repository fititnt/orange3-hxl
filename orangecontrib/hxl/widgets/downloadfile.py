from dataclasses import dataclass
# from Orange.evaluation.testing import Results
# import Orange.evaluation
# import numpy
import logging
from typing import List, Optional
from Orange.data import Table
from Orange.widgets import gui
from Orange.widgets.settings import Setting
from Orange.widgets.widget import OWWidget, Input, Output, Msg

import concurrent.futures
from Orange.widgets.utils.concurrent import ThreadExecutor, FutureWatcher, methodinvoke
from Orange.widgets.utils.widgetpreview import WidgetPreview
from AnyQt.QtCore import Qt, QThread, pyqtSlot
from AnyQt.QtWidgets import \
    QStyle, QComboBox, QMessageBox, QGridLayout, QLabel, \
    QLineEdit, QSizePolicy as Policy, QCompleter
from functools import reduce, partial
from Orange.widgets.utils.concurrent import ConcurrentWidgetMixin, TaskState

from orangecontrib.hxl.base import FileRAW
from orangecontrib.hxl.vars import RESOUCE_ALIAS__HELP, RESOUCE_URI_FALLBACK__HELP, RESOUCE_VALIDATE_HAVESTRING__PLACEHOLDER, RESOUCE_VALIDATE_MIMETYPES__PLACEHOLDER, RESOUCE_VALIDATE_NOTHAVESTRING__PLACEHOLDER, RESOURCE_DATAVAULT_CACHE_TTL, RESOURCE_DATAVAULT_CACHE_TTL__HELP, RESOURCE_DATAVAULT_CACHING_KIND, RESOURCE_DATAVAULT_CACHING_KIND__HELP
from orangecontrib.hxl.widgets.mixin import HXLWidgetFeedbackMixin
from orangecontrib.hxl.widgets.utils import hash_intentionaly_weak

from orangecontrib.hxl.base import DataVault

log = logging.getLogger(__name__)


class HXLDownloadFile(OWWidget, HXLWidgetFeedbackMixin):
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

    res_alias = Setting("", schema_only=True)
    res_hash = Setting("", schema_only=True)
    res_cache_kind = Setting("", schema_only=True)
    res_cache_ttl = Setting("", schema_only=True)
    res_valid_mimetypes = Setting("", schema_only=True)
    res_valid_havestring = Setting("", schema_only=True)
    res_valid_nothavestring = Setting("", schema_only=True)
    ui_pro = Setting(False)
    source_uri_main = Setting("", schema_only=True)
    source_uri_alt = Setting("", schema_only=True)
    source_uri_alt2 = Setting("", schema_only=True)

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
        primary_source_fail = Msg("Primary source failed, using backup")

    # class Error(OWWidget.Error):
    #     file_not_found = Msg("No source and altenatives ")
    #     missing_reader = Msg("Missing reader.")
    #     sheet_error = Msg("Error listing available sheets.")
    #     unknown = Msg("Read error:\n{}")

    def __init__(self):
        super().__init__()
        self.data = None

        self.vault = DataVault()
        self.fileraw = FileRAW()

        self._init_ui()

        # self.res_hash_box.setDisabled(True)

        # log.exception('downloadfile init')

        # res_alias = self.res_alias_box.text()
        res_uri = self.main_uri_box.text()
        res_hash = str(hash_intentionaly_weak(res_uri))

        # #: The current evaluating task (if any)
        # self._task = None  # type: Optional[HXLDownloadFileTask]
        # #: An executor we use to submit learner evaluations into a thread pool
        # self._executor = ThreadExecutor()

        # progress = gui.ProgressBar(self)

        if DataVault.resource_summary('rawinput', res_hash) is not None:
            # log.exception('downloadfile init already exist, sending rigth now')
            self.commit()
            # self.commit.deferred()
            # self.commit.now()

    def _init_ui(self):

        self.controlArea.setMinimumWidth(900)

        #self.controlArea.setSizePolicy(Policy.Expanding, Policy.Fixed)

        self.action_box = gui.widgetBox(
            self.controlArea, "Actions")

        #self.action_box.setSizePolicy(Policy.Expanding, Policy.Fixed)

        # self.action_p1_box = gui.widgetBox(
        #     self.action_box, False, Qt.Horizontal)
        self.action_p1_box = gui.hBox(
            self.action_box)

        self.res_cache_kind_combo = QComboBox(self)
        for _label, _value in RESOURCE_DATAVAULT_CACHING_KIND.items():
            self.res_cache_kind_combo.addItem(_label, _value)

        self.res_cache_kind_combo.setToolTip(
            RESOURCE_DATAVAULT_CACHING_KIND__HELP)
        self.action_p1_box.layout().addWidget(self.res_cache_kind_combo)

        self.res_cache_ttl_combo = QComboBox(self)
        for _label, _value in RESOURCE_DATAVAULT_CACHE_TTL.items():
            self.res_cache_ttl_combo.addItem(_label, _value)

        self.res_cache_ttl_combo.setToolTip(RESOURCE_DATAVAULT_CACHE_TTL__HELP)
        self.action_p1_box.layout().addWidget(self.res_cache_ttl_combo)

        gui.checkBox(
            self.action_p1_box, master=self,
            value='ui_pro', label="Advanced",
            labelWidth=0,
            callback=self._init_ui_refresh)

        self.main_uri_box = gui.lineEdit(
            self.action_box, self, "source_uri_main",
            orientation=Qt.Horizontal,
            label="URL of source",
            callback=None)

        gui.separator(self.action_box)

        self.action_p2_box = gui.vBox(
            self.action_box)
        self.action_p2_box.hide()

        self.alt_uri_box = gui.lineEdit(
            self.action_p2_box, self, "source_uri_alt",
            label="URI Failback 1",
            orientation=Qt.Horizontal,
            callback=None)

        self.alt_uri_box.setToolTip(RESOUCE_URI_FALLBACK__HELP)

        # alt_uri_box_policy = self.alt_uri_box
        # alt_uri_box_policy.setHorizontalPolicy(Policy.Expanding)
        # self.alt_uri_box.setSizePolicy(alt_uri_box_policy)

        self.alt2_uri_box = gui.lineEdit(
            self.action_p2_box, self, "source_uri_alt2",
            orientation=Qt.Horizontal,
            label="URI Failback 2", callback=None)

        self.alt2_uri_box.setToolTip(RESOUCE_URI_FALLBACK__HELP)

        self.res_alias_box = gui.lineEdit(
            self.action_p2_box, self, "res_alias",
            orientation=Qt.Horizontal, label="Alias (used as hash reference)")

        self.res_alias_box.setToolTip(RESOUCE_ALIAS__HELP)

        self.resource_validation_box = gui.widgetBox(
            self.action_p2_box, "Validation")

        self.res_valid_havestring_box = gui.lineEdit(
            self.resource_validation_box, self, "res_valid_havestring",
            orientation=Qt.Horizontal,
            label="Must have text", callback=None)

        self.res_valid_havestring_box.setPlaceholderText(
            RESOUCE_VALIDATE_HAVESTRING__PLACEHOLDER
        )

        self.res_valid_nothavestring_box = gui.lineEdit(
            self.resource_validation_box, self, "res_valid_nothavestring",
            orientation=Qt.Horizontal,
            label="Must NOT have text", callback=None)

        self.res_valid_nothavestring_box.setPlaceholderText(
            RESOUCE_VALIDATE_NOTHAVESTRING__PLACEHOLDER
        )

        self.res_valid_mimetypes_box = gui.lineEdit(
            self.resource_validation_box, self, "res_valid_mimetypes",
            orientation=Qt.Horizontal,
            label="Mime types", callback=None)

        self.res_valid_mimetypes_box.setPlaceholderText(
            RESOUCE_VALIDATE_MIMETYPES__PLACEHOLDER
        )

        gui.button(
            self.action_box, self, "(Re)Download", callback=self.commit_forced)

        # gui.separator(self.controlArea)
        #self.optionsBox = gui.widgetBox(self.controlArea, "Options")

        #self.optionsBox.setSizePolicy(Policy.Expanding, Policy.Fixed)

        # self.res_hash_box.setText('teste')

        gui.separator(self.controlArea)
        self.infos_box = gui.widgetBox(
            self.controlArea, "Detailed information")
        self.infos_box.setSizePolicy(Policy.Expanding, Policy.Fixed)

        self.browse_button = gui.button(
            self.infos_box, self, "Browse",
            callback=self.browse_active)

        box = gui.widgetBox(self.infos_box, "Info")

        # self.box.setSizePolicy(Policy.Expanding, Policy.Fixed)
        self.infoa = gui.widgetLabel(box, "No comments")

        self.res_hash_box = gui.lineEdit(
            self.infos_box, self, "res_hash",
            box="Internal ID (based on alias or main source URL)")

        self._init_ui_refresh()

    def _init_ui_refresh(self):
        if self.ui_pro:
            self.res_alias_box.setDisabled(False)
            # self.res_alias_box.show()
            self.alt_uri_box.setDisabled(False)
            # self.alt_uri_box.show()
            self.alt2_uri_box.setDisabled(False)
            # self.alt2_uri_box.show()
            self.action_p2_box.show()
        else:
            self.res_alias_box.setDisabled(True)
            # self.res_alias_box.hide()
            self.alt_uri_box.setDisabled(True)
            # self.alt_uri_box.hide()
            self.alt2_uri_box.setDisabled(True)
            # self.alt2_uri_box.hide()
            self.action_p2_box.hide()

    # @gui.deferred
    # def commit(self) -> None:
    #     self.Error.clear()
    #     self.Warning.clear()
    #     if self.data:
    #         self.start(_run, self.data, self.result)

    # @gui.deferred

    def commit(self, forced=False, ttl: int = None):
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

        result = self.vault.download_resource(
            res_uri, res_hash, res_alias, use_cache=True)

        # if forced:
        #     result = self.vault.download_resource(
        #         res_uri, res_hash, res_alias, use_cache=not forced)

        #     self.infoa.setText('result download_resource ' + str(result))
        # else:
        #     result = self.vault.download_resource(
        #         res_uri, res_hash, res_alias, use_cache=not forced)
        #     self.infoa.setText(
        #         '(forced) result download_resource ' + str(result))

        self.fileraw.set_resource(res_hash, 'rawinput')

        raw_info = self.vault.resource_detail(
            self.fileraw
        )

        if raw_info and 'base' in raw_info:
            self._base_active = raw_info['base']
            self.browse_button.setText(f'Browse {str(self._base_active)}')

        # self.start(
        #     run_v2,
        #     self.vault,
        #     self.fileraw,
        #     res_uri, res_hash, res_alias
        # )

        # self.Outputs.data.send(self.data)
        # self.Outputs.data.send(self.fileraw)
        self.Outputs.fileraw.send(self.fileraw)

    def commit_forced(self):
        if not self.source_uri_main or len(self.source_uri_main) < 10:
            QMessageBox.warning(
                self,
                "Remote URI of main source",
                "Please define a value before forcing (re)download")
            return None

        self.commit(forced=True)
        # self.Warning.primary_source_fail()
        # pass

    def send_report(self):
        """send_report"""
        # self.report_plot() includes visualizations in the report
        self.report_caption(self.label)


def run_v2(
        vault: DataVault,
        fileraw: FileRAW,
        res_uri: str,
        res_hash: str,
        res_alias: str,

        state: TaskState
    # ) -> Table:
) -> FileRAW:
    if not vault or not fileraw or not res_uri:
        return None

    results = {}
    # results = fileraw
    # results = Table()
    # results = Table()

    # Define progress callback
    def callback(i: float, status=""):
        state.set_progress_value(i * 100)
        if status:
            state.set_status(status)
        if state.is_interruption_requested():
            raise Exception

    return results


@dataclass
class Result:
    # group_by: OrangeTableGroupBy = None
    result_table: Optional[Table] = None


def _run(
    data: Table,
    # group_by_attrs: List[Variable],
    # aggregations: Dict[Variable, Set[str]],
    result: Result,
    state: TaskState,
) -> Result:
    def progress(part):
        state.set_progress_value(part * 100)
        if state.is_interruption_requested():
            raise Exception

    state.set_status("Aggregating")
    # group table rows
    # if result.group_by is None:
    #     result.group_by = data.groupby(group_by_attrs)
    state.set_partial_result(result)

    # aggregations = {
    #     var: [
    #         (agg, AGGREGATIONS[agg].function)
    #         for agg in sorted(aggs, key=AGGREGATIONS_ORD.index)
    #     ]
    #     for var, aggs in aggregations.items()
    # }
    # result.result_table = result.group_by.aggregate(
    #     aggregations, wrap_callback(progress, 0.2, 1)
    # )
    return result


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


if __name__ == "__main__":
    from Orange.widgets.utils.widgetpreview import WidgetPreview  # since Orange 3.20.0
    WidgetPreview(HXLDownloadFile).run()
