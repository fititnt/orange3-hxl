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

        # layout = QGridLayout()
        # layout.setSpacing(4)
        # layout.minimumHeightForWidth(300)
        # layout.SetMinimumSize(QSize(300, 300))
        # layout.SetMinimumSize = QSize(300, 300)
        # layout.setMinimumHeight = QSize(300, 300)

        self.setMinimumWidth(300)
        self.setMinimumHeight(300)
        self.setMaximumWidth(1200)
        self.setMaximumHeight(1000)
        # layout.setMinimumWidth(300)
        # layout.setMinimumHeight(300)

        self.reader_combo = QComboBox(self)
        self.reader_combo.setSizePolicy(Policy.Expanding, Policy.Fixed)
        self.reader_combo.setMinimumSize(QSize(300, 1))
        for item in LOCALLOAD_READERS.keys():
            self.reader_combo.addItem(item)
        # self.reader_combo.activated[int].connect(self.select_reader)

        log.exception('HXLLoadLocal init')

        self.optionsBox = gui.widgetBox(self.controlArea, "Options")

        gui.button(self.optionsBox, self, "Reload", callback=self.commit)
        gui.separator(self.controlArea)

        box = gui.widgetBox(self.controlArea, "Info")
        self.infoa = gui.widgetLabel(box, "No comments")

        # layout = QGridLayout()
        # layout.setSpacing(4)
        # gui.widgetBox(self.controlArea, orientation=layout, box='Source')
        # vbox = gui.radioButtons(None, self, "source", box=True,
        #                         callback=None, addToLayout=False)
        # box = gui.vBox(self.controlArea, "Info")
        # self.infolabel = gui.widgetLabel(box, 'No data loaded.')

        # box = gui.widgetBox(self.controlArea, "Columns (Double click to edit)")
        # self.domain_editor = DomainEditor(self)
        # self.editor_model = self.domain_editor.model()
        # box.layout().addWidget(self.domain_editor)
    # @Inputs.data
    # def set_data(self, data):
    #     """set_data"""
    #     if data:
    #         self.data = data
    #     else:
    #         self.data = None

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

        _action = self.reader_combo.currentText()

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

        self.infoa.setText(json.dumps(
            _info, indent=4, sort_keys=True, ensure_ascii=False,
            default=_vars))

        # import pandas
        # # _info = inspect(pandas.read_table)
        # _info = [inspect.signature(pandas.read_table)]
        # _info.append(inspect.getdoc(pandas.read_table))
        # self.infoa.setText(json.dumps(
        #     _info, indent=4, sort_keys=True, ensure_ascii=False,
        #     default=_vars))
        # log.exception(_info)
        self.Outputs.data_frame.send(self.data_frame)
        self.Outputs.data.send(self.data)

    def send_report(self):
        """send_report"""
        # self.report_plot() includes visualizations in the report
        self.report_caption(self.label)


if __name__ == "__main__":
    from Orange.widgets.utils.widgetpreview import WidgetPreview  # since Orange 3.20.0
    WidgetPreview(HXLLoadLocal).run()
