import logging
from Orange.data import Table
from Orange.widgets import gui
from Orange.widgets.settings import Setting
from Orange.widgets.widget import OWWidget, Input, Output, Msg

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

    def send_report(self):
        """send_report"""
        # self.report_plot() includes visualizations in the report
        self.report_caption(self.label)


if __name__ == "__main__":
    from Orange.widgets.utils.widgetpreview import WidgetPreview  # since Orange 3.20.0
    WidgetPreview(HXLDownloadFile).run()
