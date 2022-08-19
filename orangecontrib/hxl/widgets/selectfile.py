import logging

from Orange.data import Table
from Orange.widgets import gui
from Orange.widgets.settings import Setting
from Orange.widgets.widget import OWWidget, Input, Output, Msg

from orangecontrib.hxl.base import FileRAW, FileRAWCollection
from orangecontrib.hxl.widgets.utils import string_to_list

log = logging.getLogger(__name__)


class HXLSelectFile(OWWidget):
    """HXLSelectFile"""
    # Widget needs a name, or it is considered an abstract widget
    # and not shown in the menu.
    name = "Select Raw File"
    id = "orangecontrib.hxl.widgets.selectfile"
    description = """
    [DRAFT] From a local FileRAWCollection, select an FileRAW
    """
    icon = "icons/mywidget.svg"
    priority = 70  # where in the widget order it will appear
    category = "Orange3-HXLvisualETL"
    keywords = ["widget", "data"]
    want_main_area = False
    resizing_enabled = True

    label = Setting("")
    # we will use numbers, since maybe in the future we migth enable more than one channel

    sel_f_0_name = Setting("")
    sel_f_0_ext = Setting("")

    class Inputs:
        """Inputs"""
        # specify the name of the input and the type
        # data = Input("Data", Table)
        # data = Input("FileRAWCollection", FileRAWCollection)
        filerawcollection = Input(
            "FileRAWCollection", FileRAWCollection)

    class Outputs:
        """Outputs"""
        # if there are two or more outputs, default=True marks the default output
        # data = Output("Data", Table, default=True, auto_summary=False)
        # data = Output("FileRAW", FileRAW, default=True, auto_summary=False)
        fileraw = Output("FileRAW", FileRAW)

    # same class can be initiated for Error and Information messages
    class Warning(OWWidget.Warning):
        """Warning"""
        warning = Msg("My warning!")

    def __init__(self):
        super().__init__()
        self.filerawcollection = None
        self.fileraw = None

        self.action_box = gui.widgetBox(
            self.controlArea, "Default Selection")

        self.sel_f_0_ext_box = gui.lineEdit(
            self.action_box, self, "sel_f_0_ext",
            box="Extension (use | to multiple)",
            callback=self.commit
        )

        self.sel_f_0_name_box = gui.lineEdit(
            self.action_box, self, "sel_f_0_name",
            box="Name (accepts regex)",
            callback=self.commit
        )

        # self.action_box.layout().addWidget(self.label_box)
        gui.button(self.action_box, self, "Reload", callback=self.commit)
        # log.exception('HXLSelectFile init')

        if self.filerawcollection is not None:
            # log.exception(
            #     f'unzipfile init something already ready ... [{str(self.data)}][{str(self.fileraw)}]')
            log.exception(
                f'HXLSelectFile init something already ready ... [{str(self.filerawcollection)}]')
            self.commit()

    @Inputs.filerawcollection
    def set_filerawcollection(self, filerawcollection):
        """set_data"""
        if filerawcollection:
            self.filerawcollection = filerawcollection
            self.commit()
        else:
            self.filerawcollection = None

    def commit(self):
        """commit"""
        if not self.filerawcollection or not self.filerawcollection.ready():
            # log.exception('HXLSelectFile commit not ready yet')
            return None

        extensions = string_to_list(self.sel_f_0_ext, default = None)
        filenames = self.sel_f_0_name if self.sel_f_0_name else None
        if filenames:
            filenames = [filenames]
        # if self.sel_f_0_ext:

        fileraw = self.filerawcollection.select(
            extensions=extensions,
            filenames=filenames,
        )
        # log.exception(f'HXLSelectFile commit [{str(filenames)}]')
        self.Outputs.fileraw.send(fileraw)

    def send_report(self):
        """send_report"""
        # self.report_plot() includes visualizations in the report
        self.report_caption(self.label)


if __name__ == "__main__":
    from Orange.widgets.utils.widgetpreview import WidgetPreview  # since Orange 3.20.0
    WidgetPreview(HXLSelectFile).run()
