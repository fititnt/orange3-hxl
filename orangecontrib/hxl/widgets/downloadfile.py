from Orange.data import Table
from Orange.widgets import gui
from Orange.widgets.settings import Setting
from Orange.widgets.widget import OWWidget, Input, Output, Msg

from orangecontrib.hxl.base import FileRAW


class HXLDownloadFile(OWWidget):
    """HXLDownloadFile"""
    # Widget needs a name, or it is considered an abstract widget
    # and not shown in the menu.
    name = "Download Raw File"
    id = "orangecontrib.hxl.widgets.downloadfile"
    description = """
    [DRAFT] Download remote resource into a local FileRAW
    """
    icon = "icons/mywidget.svg"
    priority = 50  # where in the widget order it will appear
    category = "Orange3-HXLvisualETL"
    keywords = ["widget", "data"]
    want_main_area = False
    resizing_enabled = False

    res_id = Setting("")
    res_hash = Setting("")
    source_uri_main = Setting("")
    source_uri_alt = Setting("")
    source_uri_alt2 = Setting("")

    # class Inputs:
    #     """Inputs"""
    #     # specify the name of the input and the type
    #     data = Input("Data", Table)

    class Outputs:
        """Outputs"""
        # if there are two or more outputs, default=True marks the default output
        # data = Output("Data", Table, default=True, auto_summary=False)
        data = Output("FileRAW", FileRAW, default=True, auto_summary=False)

    # same class can be initiated for Error and Information messages
    class Warning(OWWidget.Warning):
        """Warning"""
        warning = Msg("My warning!")

    def __init__(self):
        super().__init__()
        self.data = None

        self.res_id_box = gui.lineEdit(
            self.controlArea, self, "res_id", box="Friendly alias (optional)")

        self.res_hash_box = gui.lineEdit(
            self.controlArea, self, "res_hash", box="Internal hash")
        self.res_hash_box.setDisabled(True)

        self.main_uri_box = gui.lineEdit(
            self.controlArea, self, "source_uri_main", box="Remote URI of main source", callback=self.commit)

        self.alt_uri_box = gui.lineEdit(
            self.controlArea, self, "source_uri_alt", box="Remote URI, backup alternative 1", callback=self.commit)

        self.alt2_uri_box = gui.lineEdit(
            self.controlArea, self, "source_uri_alt2", box="Remote URI, backup alternative 2", callback=self.commit)

        gui.separator(self.controlArea)
        self.optionsBox = gui.widgetBox(self.controlArea, "Options")

        gui.button(self.optionsBox, self, "(Re)Download", callback=self.commit)

        self.res_hash_box.setText('teste')

        # self.optionsBox.setDisabled(False)

    # @Inputs.data
    # def set_data(self, data):
    #     """set_data"""
    #     if data:
    #         self.data = data
    #     else:
    #         self.data = None

    def commit(self):
        """commit"""
        self.Outputs.data.send(self.data)

    def send_report(self):
        """send_report"""
        # self.report_plot() includes visualizations in the report
        self.report_caption(self.label)


if __name__ == "__main__":
    from Orange.widgets.utils.widgetpreview import WidgetPreview  # since Orange 3.20.0
    WidgetPreview(HXLDownloadFile).run()
