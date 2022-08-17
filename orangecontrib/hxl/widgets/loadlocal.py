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
from orangecontrib.hxl.widgets.utils import file_csv_to_pandas, file_pandas_to_table

log = logging.getLogger(__name__)

LOCALLOAD_READERS = [
    'pandas.read_csv',
    'pandas.read_json',
    'pandas.read_xml',
]


class HXLLoadLocal(OWWidget):
    # class HXLLoadLocal(OWCSVFileImport):
    # class HXLLoadLocal(_owcsvimport.OWCSVFileImport):
    """HXLLoadLocal"""
    # Widget needs a name, or it is considered an abstract widget
    # and not shown in the menu.
    name = "Load Raw File"
    id = "orangecontrib.widgets.hxl.loadlocal"
    description = """
    [DRAFT] Local an already HXLized local file
    """
    icon = "icons/mywidget.svg"
    priority = 102  # where in the widget order it will appear
    category = "Orange3-HXLvisualETL"
    keywords = ["widget", "data"]
    want_main_area = False
    resizing_enabled = False

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

        # self.label_box = gui.lineEdit(
        #     self.controlArea, self, "label", box="Text", callback=self.commit)

        self.reader_combo = QComboBox(self)
        self.reader_combo.setSizePolicy(Policy.Expanding, Policy.Fixed)
        self.reader_combo.setMinimumSize(QSize(300, 1))
        for item in LOCALLOAD_READERS:
            self.reader_combo.addItem(item)
        # self.reader_combo.activated[int].connect(self.select_reader)

        log.exception('HXLLoadLocal init')

        self.optionsBox = gui.widgetBox(self.controlArea, "Options")

        gui.button(self.optionsBox, self, "Reload", callback=self.commit)
        gui.separator(self.controlArea)

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

        self.data_frame = file_csv_to_pandas(self.fileraw.base())
        self.data = file_pandas_to_table(self.data_frame)
        self.Outputs.data_frame.send(self.data_frame)
        self.Outputs.data.send(self.data)

    def send_report(self):
        """send_report"""
        # self.report_plot() includes visualizations in the report
        self.report_caption(self.label)


if __name__ == "__main__":
    from Orange.widgets.utils.widgetpreview import WidgetPreview  # since Orange 3.20.0
    WidgetPreview(HXLLoadLocal).run()
