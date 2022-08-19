import json
from Orange.data import Table
from Orange.widgets import gui
from Orange.widgets.settings import Setting
from Orange.widgets.widget import OWWidget, Input, Output, Msg

from orangecontrib.hxl.base import DataVault

# from orangecontrib.hxl.base import FileRAW, FileRAWCollection


class HXLDataVaultConf(OWWidget):
    """HXLDataVaultConf"""
    # Widget needs a name, or it is considered an abstract widget
    # and not shown in the menu.
    name = "Data Vault Conf "
    id = "orangecontrib.hxl.widgets.vaultconf"
    description = """
    [DRAFT] Configure active local data vault configurations.
    This allows overriding defaults.
    """
    icon = "icons/mywidget.svg"
    priority = 10  # where in the widget order it will appear
    category = "Orange3-HXLvisualETL"
    keywords = ["widget", "data"]
    want_main_area = False
    resizing_enabled = False

    label = Setting("")

    # class Inputs:
    #     """Inputs"""
    #     # specify the name of the input and the type
    #     # data = Input("Data", Table)
    #     # data = Input("FileRAWCollection", FileRAWCollection)
    #     data = Input("FileRAWCollection", FileRAWCollection, auto_summary=False)

    class Outputs:
        """Outputs"""
        # if there are two or more outputs, default=True marks the default output
        data = Output("Data", Table, default=True)
        # data = Output("FileRAW", FileRAW, default=True, auto_summary=False)

    # same class can be initiated for Error and Information messages
    class Warning(OWWidget.Warning):
        """Warning"""
        warning = Msg("My warning!")

    def __init__(self):
        super().__init__()
        self.data = None

        self.vault = DataVault()

        # self.label_box = gui.lineEdit(
        #     self.controlArea, self, "label", box="Text", callback=self.commit)

        self.optionsBox = gui.widgetBox(self.controlArea, "Main Data Vault")

        box = gui.widgetBox(self.controlArea, "Info")
        self.infoa = gui.widgetLabel(
            box, 'DataVault will try initialize '
            f'{self.vault.default_data_vault}'
        )

        self.main_data_vault_button = gui.button(
            self.optionsBox, self,
            "Initialize Main DataVault",
            callback=self.initilize_data_vault
        )

        if self.vault.is_initialized():
            self.optionsBox.setDisabled(True)
            self.infoa.setText(
                f'DataVault already initialized at '
                f'{self.vault.default_data_vault}')

    # @Inputs.data
    # def set_data(self, data):
    #     """set_data"""
    #     if data:
    #         self.data = data
    #     else:
    #         self.data = None

    def commit(self):
        """commit"""
        # self.infoa.setText(json.dumps(self.__dict__))

        self.Outputs.data.send(self.data)

    def initilize_data_vault(self):
        """commit"""
        if not self.vault.is_initialized():
            self.vault.initialize()
        if self.vault.is_initialized():
            self.optionsBox.setDisabled(True)
            self.infoa.setText(
                f'Success! Local storage will be at '
                f'{self.vault.default_data_vault}')
        else:
            self.infoa.setText(
                f'Something is wrong. Not able to initialize '
                f'{self.vault.default_data_vault}')

    def send_report(self):
        """send_report"""
        # self.report_plot() includes visualizations in the report
        self.report_caption(self.label)


if __name__ == "__main__":
    from Orange.widgets.utils.widgetpreview import WidgetPreview  # since Orange 3.20.0
    WidgetPreview(HXLDataVaultConf).run()
