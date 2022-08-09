import numpy as np
import logging
from Orange.data import Table
from Orange.widgets import gui
from Orange.widgets.settings import Setting
from Orange.widgets.widget import OWWidget, Input, Output, Msg
from Orange.data import Table, Domain, DiscreteVariable, StringVariable
from Orange.data.util import SharedComputeValue, get_unique_names

from .utils import *

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

        # new_attribute = 'latitude'
        # new_column = ['aa'] * 200
        # old_domain = self.data
        # domain = Domain(old_domain.attributes + [new_attribute],
        #                 old_domain.class_vars,
        #                 old_domain.metas)
        # # table = data.transform(domain)
        # table = self.data.transform(domain)
        # table[:, new_attribute] = new_column

        var = 'qcc-Zxxx-r-pWDATA-pp625-ps5000-x-zzwgs84point'
        column = self.data.get_column_view(var)[0]
        sc = WKTPointSplit(self.data, var)

        log.exception('sc')
        log.exception(sc)

        new_columns = tuple(DiscreteVariable(
            get_unique_names(self.data.domain, v), values=("0", "1"),
            compute_value=OneHotStrings(sc, v)
        ) for v in sc.new_values)
        # new_columns = tuple(DiscreteVariable("1") for v in sc.new_values)

        # log.exception('new_columns')
        # log.exception(new_columns)

        new_domain = Domain(
            self.data.domain.attributes + new_columns,
            self.data.domain.class_vars, self.data.domain.metas
        )
        extended_data = self.data.transform(new_domain)
        self.Outputs.data.send(extended_data)

        # self.Outputs.data.send(self.data)

    def send_report(self):
        # self.report_plot() includes visualizations in the report
        self.report_caption(self.label)

    @staticmethod
    def get_string_values(data, var):
        # turn discrete to string variable
        column = data.get_column_view(var)[0]
        # if var.is_discrete:
        #     return [var.str_val(x) for x in column]
        return column


class OneHotStrings(SharedComputeValue):

    def __init__(self, fn, new_feature):
        super().__init__(fn)
        self.new_feature = new_feature

    def __eq__(self, other):
        return self.compute_shared == other.compute_shared \
            and self.new_feature == other.new_feature

    def __hash__(self):
        return hash((self.compute_shared, self.new_feature))

    def compute(self, data, shared_data):
        indices = shared_data[self.new_feature]
        col = np.zeros(len(data))
        col[indices] = 1
        return col


if __name__ == "__main__":
    from Orange.widgets.utils.widgetpreview import WidgetPreview  # since Orange 3.20.0
    WidgetPreview(HXLAuto).run()
