import logging
import json
from Orange.data import Table
from Orange.widgets import gui
from Orange.widgets.settings import Setting
from Orange.widgets.widget import OWWidget, Input, Output, Msg

from AnyQt.QtWidgets import QTextEdit, QComboBox, QSizePolicy as Policy

from orangecontrib.hxl.base import FileRAW, FileRAWCollection
from orangecontrib.hxl.transform.uncompress import uncompress_options
from orangecontrib.hxl.widgets.utils import browse_local_resource, file_unzip

log = logging.getLogger(__name__)

# UNZIP_OPTIONS =


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
        self._base_active = None

        self.action_box = gui.widgetBox(
            self.controlArea, "Actions")

        self.uncompress_combo = QComboBox(self)
        self.uncompress_combo.setSizePolicy(Policy.Expanding, Policy.Fixed)

        action_main_options = uncompress_options()

        for item, _value in action_main_options.items():
            self.uncompress_combo.addItem(item)
        self.uncompress_combo.activated[int].connect(self.gui_update_infos)
        self.action_box.layout().addWidget(self.uncompress_combo)

        # log.exception('unzipfile init')

        # self.label_box = gui.lineEdit(
        #     self.controlArea, self, "label", box="Text", callback=self.commit)

        self.infos_box = gui.widgetBox(
            self.controlArea, "Detailed information")
        self.browse_button = gui.button(
            self.infos_box, self, "Browse",
            callback=self.browse_active)

        self.feedback_box = gui.widgetBox(self.infos_box, "Feedback")
        self.feedback_box.setVisible(True)
        self.feedback = QTextEdit(self.feedback_box)
        # self.feedback.setPlainText('No specific feedback')
        self.feedback_box.layout().addWidget(self.feedback)

        # gui.separator(self.controlArea)
        # box = gui.widgetBox(self.controlArea, "Info")
        # self.infoa = gui.widgetLabel(box, "Waiting reference data")

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

    def browse_active(self):
        """browse_active"""
        if self._base_active:
            browse_local_resource(self._base_active)
        else:
            self.feedback.setPlainText('Invalid base')

    def commit(self):
        """commit"""
        # if not self.data and not self.fileraw:
        #     return None
        if not self.fileraw or self.fileraw.ready() is None:
            return None

        # log.exception(f'unzipfile commit self.fileraw  [{str(self.fileraw)}]')
        # log.exception(f'unzipfile commit self.data  [{str(self.data)}]')
        # self.infoa.setText(json.dumps([self.data, self.fileraw], default=vars))
        # self.infoa.setText(json.dumps([self.fileraw], default=vars))

        self.filerawcollection.res_hash = self.fileraw.res_hash

        if self.filerawcollection.already_ready():
            # log.exception(
            #     f'unzipfile commit already_ready [{str(self.filerawcollection)}]')
            self.Outputs.filerawcollection.send(self.filerawcollection)
            self._base_active = self.filerawcollection.base()
            self.browse_button.setText(f'Browse {str(self._base_active)}')
            return True

        file_unzip(self.fileraw.base(), self.filerawcollection.base())

        # log.exception(
        #     f'unzipfile commit self.filerawcollection.ready() [{str(self.filerawcollection.ready())}]')

        self.feedback.setPlainText(json.dumps(
            json.dumps([self.fileraw], indent=4, sort_keys=False, ensure_ascii=False, default=vars)))

        self._base_active = self.filerawcollection.base()
        self.browse_button.setText(f'Browse {str(self._base_active)}')

        if self.filerawcollection and \
                self.filerawcollection.ready() is not None:
            # @TODO fix this part
            # log.exception(
            #     f'unzipfile commit OKAY [{str(self.filerawcollection)}]')
            self.Outputs.filerawcollection.send(self.filerawcollection)
        else:
            log.exception(
                f'unzipfile commit NOT OKAY [{str(self.filerawcollection)}]')

    def gui_update_infos(self):
        """gui_update_infos"""
        pass

    def send_report(self):
        """send_report"""
        # self.report_plot() includes visualizations in the report
        self.report_caption(self.label)


if __name__ == "__main__":
    from Orange.widgets.utils.widgetpreview import WidgetPreview  # since Orange 3.20.0
    WidgetPreview(HXLUnzipFile).run()
