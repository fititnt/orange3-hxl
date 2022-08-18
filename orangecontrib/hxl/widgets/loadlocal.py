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
from AnyQt.QtWidgets import QScrollArea, QWidget, QVBoxLayout, QPushButton, QTextEdit
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
    pandas_to_table,
    # rawfile_csv_to_pandas,
    # rawfile_json_to_pandas,
    # rawfile_json_normalize_to_pandas
)
log = logging.getLogger(__name__)

LOCALLOAD_READERS = {
    '': None,
    'pandas.read_table': RawFileExporter.read_table,
    'pandas.read_csv': RawFileExporter.read_csv,
    'pandas.read_json': RawFileExporter.read_json,
    'pandas.json_normalize': RawFileExporter.json_normalize,
    'pandas.read_xml': RawFileExporter.read_xml,
}


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

    label = Setting("")

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

        self.setMinimumWidth(500)
        self.setMinimumHeight(600)
        self.setMaximumWidth(1200)
        self.setMaximumHeight(1000)

        self.exporter_combo = QComboBox(self)
        self.exporter_combo.setSizePolicy(Policy.Expanding, Policy.Fixed)
        self.exporter_combo.setMinimumSize(QSize(300, 1))
        for item in LOCALLOAD_READERS.keys():
            self.exporter_combo.addItem(item)
        self.exporter_combo.activated[int].connect(self.gui_update_infos)

        log.exception('HXLLoadLocal init')

        self.optionsBox = gui.widgetBox(self.controlArea, "Options")

        gui.button(self.optionsBox, self, "Reload", callback=self.commit)
        gui.separator(self.controlArea)

        box = gui.widgetBox(self.controlArea, "Info")
        self.infoa = gui.widgetLabel(box, "No comments")

        self.infos_box = gui.widgetBox(
            self.controlArea, "Detailed information")

        self.feedback_box = gui.widgetBox(self.infos_box, "Feedback")
        self.feedback_box.setVisible(True)
        self.feedback = QTextEdit(self.feedback_box)
        self.feedback.setPlainText('No specific feedback')
        self.feedback_box.layout().addWidget(self.feedback)

        self.help_box = gui.widgetBox(self.infos_box, "Help")
        self.help_box.setVisible(True)
        self.help = QTextEdit(self.help_box)
        self.help.setPlainText('No specific help messages')
        self.help_box.layout().addWidget(self.help)

        gui.button(self.optionsBox, self, "Orange CSVImport",
                   callback=self.show_orange_csvimport)

    @Inputs.fileraw
    def set_fileraw(self, fileraw):
        """set_fileraw"""
        if fileraw:
            self.fileraw = fileraw
            self.commit()
        else:
            self.fileraw = None

    def commit(self):
        """commit"""
        if not self.fileraw:
            return None

        log.exception('HXLLoadLocal init')

        def _vars(param):
            return str(param)

        _action = self.exporter_combo.currentText()

        if LOCALLOAD_READERS[_action] is not None:
            # self.data_frame = file_csv_to_pandas(self.fileraw.base())
            self.data_frame = LOCALLOAD_READERS[_action](self.fileraw.base())
            if self.data_frame is not None:
                self.data = pandas_to_table(self.data_frame)
            else:
                self.data = None
        else:
            # Empty
            self.data_frame = pd.DataFrame()

        _info = [
            self.fileraw,
            _action,
            self.data_frame.head() if self.data else None,
        ]

        rexpo = RawFileExporter(_action)
        log.exception(rexpo.options_of())

        self.infoa.setText(json.dumps(
            _info, indent=4, sort_keys=True, ensure_ascii=False,
            default=_vars))

        self.Outputs.data_frame.send(self.data_frame)
        self.Outputs.data.send(self.data)

    def gui_update_infos(self):
        pass

    def send_report(self):
        """send_report"""
        # self.report_plot() includes visualizations in the report
        self.report_caption(self.label)

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
