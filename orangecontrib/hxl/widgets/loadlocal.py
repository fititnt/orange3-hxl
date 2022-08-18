# from PySide6.QtCore import QAbstractItemModel, QModelIndex, QObject, Qt, QFileInfo
# from PySide6.QtWidgets import QTreeView, QApplication, QHeaderView
from typing import Any, Iterable, List, Dict, Union
import sys
import inspect
import json
import logging

from Orange.data import Table
from Orange.widgets import gui
from Orange.widgets.settings import Setting
from Orange.widgets.widget import OWWidget, Input, Output, Msg

from AnyQt.QtWidgets import \
    QStyle, QComboBox, QMessageBox, QGridLayout, QLabel, \
    QLineEdit, QSizePolicy as Policy, QCompleter
from AnyQt.QtWidgets import QScrollArea, QWidget, QVBoxLayout, QPushButton, QTextEdit, QPlainTextEdit
from AnyQt.QtCore import (
    Qt, QFileInfo, QTimer, QSettings, QObject, QSize, QMimeDatabase, QMimeType
)


# from Orange.widgets.utils.domaineditor import DomainEditor

# from Orange.widgets.data.owcsvimport import (
#     pandas_to_table
# )
import pandas as pd

# from Orange.widgets.data.owcsvimport import OWCSVFileImport as _OWCSVFileImport
# from Orange.widgets.data import owcsvimport as _owcsvimport
from orangecontrib.hxl.base import FileRAW
from orangecontrib.hxl.widgets.utils import (
    RawFileExporter,
    file_raw_info,
    pandas_to_table,
    # rawfile_csv_to_pandas,
    # rawfile_json_to_pandas,
    # rawfile_json_normalize_to_pandas
)
log = logging.getLogger(__name__)

# LOCALLOAD_READERS = {
#     '': None,
#     'pandas.read_table': RawFileExporter.read_table,
#     'pandas.read_csv': RawFileExporter.read_csv,
#     'pandas.read_json': RawFileExporter.read_json,
#     'pandas.json_normalize': RawFileExporter.json_normalize,
#     'pandas.read_xml': RawFileExporter.read_xml,
# }


class HXLLoadLocal(OWWidget):
    # class HXLLoadLocal(OWCSVFileImport):
    # class HXLLoadLocal(_owcsvimport.OWCSVFileImport):
    """HXLLoadLocal"""
    # Widget needs a name, or it is considered an abstract widget
    # and not shown in the menu.
    name = "Load Raw File"
    id = "orangecontrib.widgets.hxl.loadlocal"
    description = """
    Load a FileRAW into Orange3 Data / DataFrame
    """
    icon = "icons/mywidget.svg"
    priority = 102  # where in the widget order it will appear
    category = "Orange3-HXLvisualETL"
    keywords = ["widget", "data"]

    want_main_area = False
    # resizing_enabled = False

    openclass = True

    # label = Setting("")
    action_callable = Setting("")
    # action_args = Setting("", "#argname='Value'\n#arg2=2579")
    action_args = Setting("")
    _actions_args_placeholder = "delimiter=','\n#argname='the value'\n#arg2=2"

    class Inputs:
        """Inputs"""
        # specify the name of the input and the type
        # data = Input("Data", Table)
        fileraw = Input("FileRAW", FileRAW)
        # data = Output("FileRAW", FileRAW, default=True, auto_summary=False)

    # class Outputs:
    #     """Outputs"""
    #     # if there are two or more outputs, default=True marks the default output
    #     data = Output("Data", Table, default=True)

    class Outputs:
        data = Output(
            name="Data",
            type=Table,
            doc="Loaded data set.")
        data_frame = Output(
            name="Data Frame",
            type=pd.DataFrame,
            doc="",
            auto_summary=False
        )

    # same class can be initiated for Error and Information messages
    class Warning(OWWidget.Warning):
        """Warning"""
        warning = Msg("My warning!")

    def __init__(self):
        super().__init__()
        self.fileraw = None
        self.data = None
        # return None
        self.rawexpo = RawFileExporter()

        self.setMinimumWidth(600)
        self.setMinimumHeight(600)
        self.setMaximumWidth(1200)
        self.setMaximumHeight(1000)


        self.action_box = gui.widgetBox(
            self.controlArea, "Actions")

        self.exporter_combo = QComboBox(self)
        self.exporter_combo.setSizePolicy(Policy.Expanding, Policy.Fixed)
        # self.exporter_combo.setMinimumSize(QSize(300, 16))
        # for item in LOCALLOAD_READERS.keys():

        _options = self.rawexpo.get_all_available_options()

        log.exception(_options)

        # return None
        for item in self.rawexpo.get_all_available_options():
            self.exporter_combo.addItem(item)
        self.exporter_combo.activated[int].connect(self.gui_update_infos)
        self.action_box.layout().addWidget(self.exporter_combo)

        self.loader_args_control = QPlainTextEdit(self)
        self.loader_args_control.setPlaceholderText(
            self._actions_args_placeholder)
        # self.loader_args_control.setPlainText()
        self.action_box.layout().addWidget(self.loader_args_control)
        # self.loader_args_control.
        # # self.label_box = gui.

        gui.button(self.action_box, self, "Reload", callback=self.commit)

        # log.exception('HXLLoadLocal init')


        #gui.button(self.optionsBox, self, "Reload", callback=self.commit)
        gui.separator(self.controlArea)

        # box = gui.widgetBox(self.controlArea, "Info")
        # self.infoa = gui.widgetLabel(box, "No comments")

        self.infos_box = gui.widgetBox(
            self.controlArea, "Detailed information")


        self.help_box = gui.widgetBox(self.infos_box, "Help")
        self.help_box.setVisible(True)
        self.help = QTextEdit(self.help_box)
        self.help.setPlainText('No specific help messages')
        self.help_box.layout().addWidget(self.help)

        self.peakraw_box = gui.widgetBox(self.infos_box, "Raw input")
        self.peakraw_box.setVisible(True)
        self.peakraw = QTextEdit(self.peakraw_box)
        self.peakraw.setPlainText('No loaded yet')
        self.peakraw_box.layout().addWidget(self.peakraw)

        self.feedback_box = gui.widgetBox(self.infos_box, "Feedback")
        self.feedback_box.setVisible(True)
        self.feedback = QTextEdit(self.feedback_box)
        self.feedback.setPlainText('No specific feedback')
        self.feedback_box.layout().addWidget(self.feedback)

        self.optionsBox = gui.widgetBox(self.controlArea, "Options")
        gui.button(self.optionsBox, self, "Orange CSVImport",
                   callback=self.show_orange_csvimport)

    @Inputs.fileraw
    def set_fileraw(self, fileraw):
        """set_fileraw"""
        if fileraw:
            self.fileraw = fileraw
            self.commit()

            # @TODO only try again this if input changed
            inputraw = file_raw_info(self.fileraw.base())
            self.peakraw.setPlainText(inputraw)
        else:
            self.fileraw = None

    def commit(self):
        """commit"""
        if not self.fileraw:
            return None

        log.exception('HXLLoadLocal init')

        # Just in case, lets update the infos before
        self.gui_update_infos()

        # return None

        # def _vars(param):
        #     return str(param)

        _action = self.exporter_combo.currentText()
        _resource_path = self.fileraw.base()

        data_frame = self.rawexpo.try_run(_action, _resource_path)
        if data_frame is None:
            errors = self.rawexpo.why_failed(formated=True)
            self.data_frame = None
            self.data = None
            self.feedback.setPlainText(errors)
            # self.infoa.setText(errors)
        else:
            self.data_frame = data_frame
            self.data = pandas_to_table(self.data_frame)

        self.Outputs.data_frame.send(self.data_frame)
        self.Outputs.data.send(self.data)

    def gui_update_infos(self):

        log.exception('gui_update_infos updated')
        _action = self.exporter_combo.currentText()
        _action_args = self.loader_args_control.toPlainText()

        log.exception('_action_args')
        log.exception(_action_args)

        help_message = self.rawexpo.user_help(_action)

        # self.rawexpo.signature = _action
        # help_message = self.rawexpo.options_of(_action)
        # help_message = RawFileExporter(_action)
        self.help.setPlainText(str(help_message))
        # self.help.setPlainText(str('teste eee'))
        # log.exception(help_message)

        # if LOCALLOAD_READERS[_action] is not None:
        #     pass

        # pass

    # def send_report(self):
    #     """send_report"""
    #     # self.report_plot() includes visualizations in the report
    #     self.report_caption(self.label)

    def show_orange_csvimport(self):
        path = self.fileraw.base()
        from Orange.widgets.data.owcsvimport import CSVImportDialog
        dlg = CSVImportDialog(
            self, windowTitle="Import Options", sizeGripEnabled=True)
        dlg.setPath(path)
        dlg.show()

    def show_new_window(self, checked):
        log.exception('show_new_window called')
        w = AnotherWindow()
        w.show()


class AnotherWindow(QWidget):
    """
    This "window" is a QWidget. If it has no parent, it
    will appear as a free-floating window as we want.
    """

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.label = QLabel("Another Window")
        layout.addWidget(self.label)
        self.setLayout(layout)


if __name__ == "__main__":
    from Orange.widgets.utils.widgetpreview import WidgetPreview  # since Orange 3.20.0
    WidgetPreview(HXLLoadLocal).run()
