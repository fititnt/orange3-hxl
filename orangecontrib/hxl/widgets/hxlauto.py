import logging
from Orange.data import Table
from Orange.widgets import gui
from Orange.widgets.settings import Setting
from Orange.widgets.widget import OWWidget, Input, Output, Msg


log = logging.getLogger(__name__)


class HXLAuto(OWWidget):
    # Widget needs a name, or it is considered an abstract widget
    # and not shown in the menu.
    name = "HXL auto inference"
    # id = "orange.widgets.data.info"
    description = """
    For already HXLated input, attempt to infer some data transformations.
    Intended to be used after orange generic File or CSV input.
    """
    icon = "icons/mywidget.svg"
    priority = 100  # where in the widget order it will appear
    keywords = ["widget", "data"]
    want_main_area = False
    resizing_enabled = False

    label = Setting("")

    class Inputs:
        # specify the name of the input and the type
        data = Input("Data", Table)
        # print('input', data.types)
        # log.debug("input: %s", data)

    class Outputs:
        # if there are two or more outputs, default=True marks the default output
        data = Output("Data", Table, default=True)
        # print('output', data)
        # log.debug("output: %s", data)
        # log.exception(data, exc_info=True)

    # same class can be initiated for Error and Information messages
    class Warning(OWWidget.Warning):
        warning = Msg("My warning!")

    def __init__(self):
        super().__init__()
        self.data = None

        self.label_box = gui.lineEdit(
            self.controlArea, self, "label", box="Text", callback=self.commit)

    @Inputs.data
    def set_data(self, data):
        if data:
            self.data = data
        else:
            self.data = None

    def commit(self):
        log.debug("commit: %s", self.data)
        # log.exception(self.data.types, exc_info=True)
        log.exception('self.data.columns')
        log.exception(self.data.columns, exc_info=True)

        # @NOTE: metas = only data with data labeled as meta. Makes sense
        log.exception('self.data.metas')
        log.exception(self.data.metas, exc_info=True)
        log.exception('self.data.attributes')
        log.exception(self.data.attributes, exc_info=True)
        log.exception('self.data.ids')
        log.exception(self.data.ids, exc_info=True)

        # @NOTE: domain = headers? humm
        log.exception('self.data.domain')
        log.exception(self.data.domain, exc_info=True)
        # log.exception(self.data.get_columns(), exc_info=True)
        # log.exception(list(self.data.columns), exc_info=True)

        # @NOTE data seens to have
        #   > [data1, data2, data3, data4] {meta1, meta2, meta3, meta4}
        #   > [data1, data2, data3, data4] {meta1, meta2, meta3, meta4}
        log.exception('self.data')
        log.exception(self.data)
        log.exception('type(self.data)')
        log.exception(type(self.data))

        self.Outputs.data.send(self.data)

    def send_report(self):
        # self.report_plot() includes visualizations in the report
        self.report_caption(self.label)


if __name__ == "__main__":
    from Orange.widgets.utils.widgetpreview import WidgetPreview  # since Orange 3.20.0
    WidgetPreview(HXLAuto).run()
