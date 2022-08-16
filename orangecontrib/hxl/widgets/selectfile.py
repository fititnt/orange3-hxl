from Orange.data import Table
from Orange.widgets import gui
from Orange.widgets.settings import Setting
from Orange.widgets.widget import OWWidget, Input, Output, Msg

from orangecontrib.hxl.hxlclasses import FileRAW, FileRAWCollection

class HXLSelectFile(OWWidget):
    """HXLSelectFile"""
    # Widget needs a name, or it is considered an abstract widget
    # and not shown in the menu.
    name = "Select File"
    description = """
    [DRAFT] Select single raw file for resouces that generate more than one.
    Example: the Unzip files.
    """
    icon = "icons/mywidget.svg"
    priority = 70  # where in the widget order it will appear
    category = "HXL visual ETL"
    keywords = ["widget", "data"]
    want_main_area = False
    resizing_enabled = False

    label = Setting("")

    class Inputs:
        """Inputs"""
        # specify the name of the input and the type
        data = Input("FileRAWCollection", FileRAWCollection)

    class Outputs:
        """Outputs"""
        # if there are two or more outputs, default=True marks the default output
        data = Output("FileRAW", FileRAW, default=True)

    # same class can be initiated for Error and Information messages
    class Warning(OWWidget.Warning):
        """Warning"""
        warning = Msg("My warning!")

    def __init__(self):
        super().__init__()
        self.data = None

        self.label_box = gui.lineEdit(
            self.controlArea, self, "label", box="Text", callback=self.commit)

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
    WidgetPreview(HXLSelectFile).run()
