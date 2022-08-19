import json
import logging

from Orange.data import Table
from Orange.widgets import gui
from Orange.widgets.settings import Setting
from Orange.widgets.widget import OWWidget, Input, Output, Msg

from orangecontrib.hxl.base import FileRAW, FileRAWCollection

log = logging.getLogger(__name__)


class HXLRAWInfo(OWWidget):
    """HXLRAWInfo"""
    # Widget needs a name, or it is considered an abstract widget
    # and not shown in the menu.
    name = "RAW Info"
    id = "orangecontrib.hxl.widgets.rawinfo"
    description = """
    [DRAFT] Inspect a FileRAW or FileRAWCollection
    """
    icon = "icons/mywidget.svg"
    priority = 9996  # where in the widget order it will appear
    category = "Orange3-HXLvisualETL"
    keywords = ["widget", "data"]
    want_main_area = False
    resizing_enabled = False

    label = Setting("")

    class Inputs:
        """Inputs"""
        # specify the name of the input and the type
        # data = Input("Data", Table)
        # data = Input("FileRAWCollection", FileRAWCollection)
        fileraw = Input(
            "FileRAW", FileRAW)
        filerawcollection = Input(
            "FileRAWCollection", FileRAWCollection)

    # class Outputs:
    #     """Outputs"""
    #     # if there are two or more outputs, default=True marks the default output
    #     # data = Output("Data", Table, default=True, auto_summary=False)
    #     # data = Output("FileRAW", FileRAW, default=True, auto_summary=False)
    #     fileraw = Output("FileRAW", FileRAW)

    # same class can be initiated for Error and Information messages
    class Warning(OWWidget.Warning):
        """Warning"""
        warning = Msg("My warning!")

    def __init__(self):
        super().__init__()
        self.filerawcollection = None
        self.fileraw = None

        # self.label_box = gui.lineEdit(
        #     self.controlArea, self, "label", box="Text", callback=self.commit)

        # log.exception('HXLSelectFile init')
        box = gui.widgetBox(self.controlArea, "Info")
        self.infoa = gui.widgetLabel(box, "No comments")

    @Inputs.fileraw
    def set_fileraw(self, fileraw):
        """set_fileraw"""
        #log.exception(f'unzipfile set_fileraw [{str(fileraw)}]')
        if fileraw:
            self.fileraw = fileraw
            self.commit()
        else:
            self.fileraw = None

    @Inputs.filerawcollection
    def set_filerawcollection(self, filerawcollection):
        """set_filerawcollection"""
        if filerawcollection:
            self.filerawcollection = filerawcollection
            self.commit()
        else:
            self.filerawcollection = None

    def commit(self):
        """commit"""
        if not self.filerawcollection and not self.fileraw:
            return None
        # if not self.filerawcollection or not self.filerawcollection.ready():
        #     return None

        # fileraw = self.filerawcollection.select()
        # log.exception(
        #     f'commit @TODO [{str(self.fileraw)}][{str(self.filerawcollection)}]')
        # self.Outputs.fileraw.send(fileraw)

        raw_info = {
            'fileraw': self.fileraw,
            'filerawcollection': self.filerawcollection
        }

        # self.infoa.setText(json.dumps(raw_info))
        self.infoa.setText(json.dumps(
            raw_info, indent=4, sort_keys=True, ensure_ascii=False, default=vars))

    def send_report(self):
        """send_report"""
        # self.report_plot() includes visualizations in the report
        self.report_caption(self.label)


if __name__ == "__main__":
    from Orange.widgets.utils.widgetpreview import WidgetPreview  # since Orange 3.20.0
    WidgetPreview(HXLRAWInfo).run()
