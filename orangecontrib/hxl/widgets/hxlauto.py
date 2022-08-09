"""hxlauto"""

import logging
import numpy as np
# from Orange.data import Table
from Orange.widgets import gui
from Orange.widgets.settings import Setting
from Orange.widgets.widget import OWWidget, Input, Output, Msg
# from Orange.data import Table, Domain, DiscreteVariable, StringVariable
from Orange.data import Table, Domain, DiscreteVariable, ContinuousVariable, StringVariable
from Orange.data.util import SharedComputeValue, get_unique_names

from orangecontrib.hxl.widgets.utils import WKTPointSplit, wkt_point_split

# from .utils import *

log = logging.getLogger(__name__)


class HXLAuto(OWWidget):
    """HXLAuto"""
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
        """Inputs"""
        # specify the name of the input and the type
        data = Input("Data", Table)
        # print('input', data.types)
        # log.debug("input: %s", data)

    class Outputs:
        """Outputs"""
        # if there are two or more outputs, default=True marks the default output
        data = Output("Data", Table, default=True)
        # print('output', data)
        # log.debug("output: %s", data)
        # log.exception(data, exc_info=True)

    # same class can be initiated for Error and Information messages
    class Warning(OWWidget.Warning):
        """Warning"""
        warning = Msg("My warning!")

    def __init__(self):
        super().__init__()
        self.data = None

        self.label_box = gui.lineEdit(
            self.controlArea, self, "label", box="Text", callback=self.commit)

    @Inputs.data
    def set_data(self, data):
        """set_data"""
        if data:
            self.data = data
        else:
            self.data = None

    def commit(self):
        """commit"""
        log.debug("commit: %s", self.data)

        var = 'qcc-Zxxx-r-pWDATA-pp625-ps5000-x-zzwgs84point'
        column = self.data.get_column_view(var)[0]
        new_column_lat = []
        new_column_lon = []
        for item in column:
            res = wkt_point_split(item)
            new_column_lat.append(res[0])
            new_column_lon.append(res[1])

        # sc = WKTPointSplit(self.data, var)

        log.exception('type(column)')
        log.exception(type(column))
        log.exception('column')
        log.exception(column)

        # log.exception('sc')
        # log.exception(sc)

        # new_columns = tuple(DiscreteVariable(
        #     get_unique_names(self.data.domain, v), values=("0", "1"),
        #     compute_value=OneHotStrings(sc, v)
        # ) for v in sc.new_values)

        log.exception('new_column_lat')
        log.exception(new_column_lat)
        log.exception('new_column_lon')
        log.exception(new_column_lon)

        # new_columns_v2 = (
        #     DiscreteVariable('latitude', new_column_lat, compute_value=True),
        #     DiscreteVariable('longitude', new_column_lon, compute_value=True),
        # # )
        # new_columns_v2 = (
        #     DiscreteVariable('latitude', values=new_column_lat),
        #     DiscreteVariable('longitude', values=new_column_lon),
        # )
        # new_columns_v2 = (
        #     StringVariable('latitude', values=new_column_lat),
        #     StringVariable('longitude', values=new_column_lon),
        # )
        new_columns_v2 = (
            ContinuousVariable('latitude'),
            ContinuousVariable('longitude'),
        )
        # new_columns = tuple(DiscreteVariable("1") for v in sc.new_values)

        log.exception('new_columns_v2')
        log.exception(new_columns_v2)

        # log.exception('new_columns')
        # log.exception(new_columns)

        # new_domain = Domain(
        #     self.data.domain.attributes + new_columns,
        #     self.data.domain.class_vars, self.data.domain.metas
        # )

        # @TODO add the values, not just the metadata
        new_domain = Domain(
            self.data.domain.attributes + new_columns_v2,
            self.data.domain.class_vars, self.data.domain.metas
        )
        extended_data = self.data.transform(new_domain)
        self.Outputs.data.send(extended_data)

        # self.Outputs.data.send(self.data)

    def send_report(self):
        """send_report"""
        # self.report_plot() includes visualizations in the report
        self.report_caption(self.label)

    @staticmethod
    def get_string_values(data, var):
        """get_string_values"""
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
