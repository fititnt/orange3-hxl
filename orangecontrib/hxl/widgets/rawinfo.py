import json
import logging
import os
from pathlib import Path

from Orange.data import Table
from Orange.widgets import gui
from Orange.widgets.settings import Setting
from Orange.widgets.widget import OWWidget, Input, Output, Msg

from AnyQt.QtWidgets import QTextEdit

from orangecontrib.hxl.base import DataVault, FileRAW, FileRAWCollection
from orangecontrib.hxl.widgets.utils import browse_local_resource

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
    resizing_enabled = True

    vault: DataVault = None

    # label = Setting("")

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
        self.vault = DataVault()

        self.setMinimumWidth(600)
        self.setMinimumHeight(600)
        self.setMaximumWidth(1200)
        self.setMaximumHeight(1000)

        self.action_box = gui.widgetBox(
            self.controlArea, "Actions")

        gui.button(self.action_box, self, "Reload info", callback=self.commit)

        self._base_active = None

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

    @Inputs.fileraw
    def set_fileraw(self, fileraw):
        """set_fileraw"""
        #log.exception(f'unzipfile set_fileraw [{str(fileraw)}]')
        if fileraw:
            self.fileraw = fileraw

            # @TODO does exist some way to check if user have the windown
            #       open? If yes, then we could autocommit, for now is
            #       commented out
            # self.commit()
        else:
            self.fileraw = None

    @Inputs.filerawcollection
    def set_filerawcollection(self, filerawcollection):
        """set_filerawcollection"""
        if filerawcollection:
            self.filerawcollection = filerawcollection

            # @TODO does exist some way to check if user have the windown
            #       open? If yes, then we could autocommit, for now is
            #       commented out
            # self.commit()
        else:
            self.filerawcollection = None

    def browse_active(self):
        """browse_active"""
        if self._base_active:
            browse_local_resource(self._base_active)
        else:
            self.feedback.setPlainText('Invalid base')

    def commit(self):
        """commit"""
        if not self.filerawcollection and not self.fileraw:
            return None
        # if not self.filerawcollection or not self.filerawcollection.ready():
        #     return None

        # fileraw = self.filerawcollection.select()
        log.exception(
            f'commit @TODO [{str(self.fileraw)}][{str(self.filerawcollection)}]')
        # self.Outputs.fileraw.send(fileraw)

        if self.filerawcollection:
            raw_info = self.vault.resource_detail(
                self.filerawcollection
            )
            # raw_info = {'todo': 'todoo'}
        else:
            raw_info = self.vault.resource_detail(
                self.fileraw)

        if raw_info and 'base' in raw_info:
            self._base_active = raw_info['base']
            self.browse_button.setText(f'Browse {str(self._base_active)}')
        else:
            self.browse_button.setText(f'Browse')
            self._base_active = None

        self.feedback.setPlainText(json.dumps(
            raw_info, indent=4, sort_keys=False, ensure_ascii=False, default=vars))

    def send_report(self):
        """send_report"""
        # self.report_plot() includes visualizations in the report
        self.report_caption(self.label)


if __name__ == "__main__":
    from Orange.widgets.utils.widgetpreview import WidgetPreview  # since Orange 3.20.0
    WidgetPreview(HXLRAWInfo).run()
