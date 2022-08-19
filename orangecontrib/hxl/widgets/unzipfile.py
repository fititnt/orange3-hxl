import logging
import json
from Orange.data import Table
from Orange.widgets import gui
from Orange.widgets.settings import Setting
from Orange.widgets.widget import OWWidget, Input, Output, Msg

from orangecontrib.hxl.base import FileRAW, FileRAWCollection
from orangecontrib.hxl.widgets.utils import file_unzip

log = logging.getLogger(__name__)


class HXLUnzipFile(OWWidget):
    """HXLUnzipFile"""
    # Widget needs a name, or it is considered an abstract widget
    # and not shown in the menu.
    name = "Unzip Raw File"
    id = "orangecontrib.hxl.widgets.unzipfile"
    description = """
    [DRAFT] Unzip (zip, gzip, bzip, ...) an FileRAW into an FileRAWCollection 
    """
    icon = "icons/mywidget.svg"
    priority = 60  # where in the widget order it will appear
    category = "Orange3-HXLvisualETL"
    keywords = ["widget", "data"]
    want_main_area = False
    resizing_enabled = False

    label = Setting("")

    # source = None
    # target = None

    class Inputs:
        """Inputs"""
        # specify the name of the input and the type
        # data = Input("Data", Table)
        # data = Input("FileRAW", FileRAW, auto_summary=False)
        fileraw = Input("FileRAW", FileRAW)
        # log.exception('unzipfile class part Inputs')

    class Outputs:
        """Outputs"""
        # if there are two or more outputs, default=True marks the default output
        # data = Output("Data", Table, default=True, auto_summary=False)
        #data = Output("FileRAW", FileRAW, default=True, auto_summary=False)
        # data = Output("FileRAWCollection", FileRAWCollection,
        #               default=True)
        filerawcollection = Output("FileRAWCollection", FileRAWCollection,
                                   default=True)

    # same class can be initiated for Error and Information messages
    class Warning(OWWidget.Warning):
        """Warning"""
        warning = Msg("My warning!")

    def __init__(self):
        super().__init__()
        # self.data = None
        # self.source = None
        self.fileraw = None
        self.filerawcollection = FileRAWCollection()
        # self.target = None

        # log.exception('unzipfile init')

        # self.label_box = gui.lineEdit(
        #     self.controlArea, self, "label", box="Text", callback=self.commit)

        gui.separator(self.controlArea)
        box = gui.widgetBox(self.controlArea, "Info")
        self.infoa = gui.widgetLabel(box, "Waiting reference data")

        # if self.data is not None or self.fileraw is not None:
        if self.fileraw is not None:
            # log.exception(
            #     f'unzipfile init something already ready ... [{str(self.data)}][{str(self.fileraw)}]')
            log.exception(
                f'unzipfile init something already ready ... [{str(self.fileraw)}]')
            self.commit()

    # @Inputs.data
    # def set_data(self, data):
    #     log.exception(f'unzipfile set_data ... [{str(data)}]')
    #     """set_data"""
    #     if data:
    #         self.data = data
    #         # self.infoa.setText(json.dumps(self.__dict__))
    #     else:
    #         self.data = None

    @Inputs.fileraw
    def set_fileraw(self, fileraw):
        """set_fileraw"""

        # log.exception(f'unzipfile set_fileraw [{str(fileraw)}]')
        if fileraw:
            self.fileraw = fileraw
            self.commit()
        else:
            self.fileraw = None

    def commit(self):
        """commit"""
        # if not self.data and not self.fileraw:
        #     return None
        if not self.fileraw or self.fileraw.ready() is None:
            return None

        # log.exception(f'unzipfile commit self.fileraw  [{str(self.fileraw)}]')
        # log.exception(f'unzipfile commit self.data  [{str(self.data)}]')
        # self.infoa.setText(json.dumps([self.data, self.fileraw], default=vars))
        self.infoa.setText(json.dumps([self.fileraw], default=vars))

        self.filerawcollection.res_hash = self.fileraw.res_hash

        if self.filerawcollection.already_ready():
            # log.exception(
            #     f'unzipfile commit already_ready [{str(self.filerawcollection)}]')
            self.Outputs.filerawcollection.send(self.filerawcollection)
            return True

        file_unzip(self.fileraw.base(), self.filerawcollection.base())

        # log.exception(
        #     f'unzipfile commit self.filerawcollection.ready() [{str(self.filerawcollection.ready())}]')

        if self.filerawcollection and \
                self.filerawcollection.ready() is not None:
            # @TODO fix this part
            # log.exception(
            #     f'unzipfile commit OKAY [{str(self.filerawcollection)}]')
            self.Outputs.filerawcollection.send(self.filerawcollection)
        else:
            log.exception(
                f'unzipfile commit NOT OKAY [{str(self.filerawcollection)}]')

    def send_report(self):
        """send_report"""
        # self.report_plot() includes visualizations in the report
        self.report_caption(self.label)


if __name__ == "__main__":
    from Orange.widgets.utils.widgetpreview import WidgetPreview  # since Orange 3.20.0
    WidgetPreview(HXLUnzipFile).run()
