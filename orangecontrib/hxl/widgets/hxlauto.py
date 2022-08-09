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

        # @TODO make this part not hardcoded

        log.exception('self.data.domain.variables')
        log.exception(self.data.domain.variables)

        # var_names = map(lambda x: x['name'], self.data.domain.variables)

        zzwgs84point = []
        already_have_latlon = False

        for item in self.data.domain.variables:
            if item.name in ['latitude', 'longitude']:
                already_have_latlon = True
            if item.name.find('zzwgs84point') > -1:
                zzwgs84point.append(item.name)

        for item in self.data.domain.metas:
            if item.name in ['latitude', 'longitude']:
                already_have_latlon = True
            if item.name.find('zzwgs84point') > -1:
                zzwgs84point.append(item.name)

        log.exception('zzwgs84point 0')
        log.exception(zzwgs84point)

        # Either not have Point(12.34 56.78) or already processed
        if len(zzwgs84point) == 0 or already_have_latlon:
            self.Outputs.data.send(self.data)
            return None

        if len(zzwgs84point) > 1:
            log.exception(
                "@TODO not implemented yet with more than one zzwgs84point")
            # return None

        # log.exception('var_names')
        # log.exception(var_names)
        log.exception('zzwgs84point')
        log.exception(zzwgs84point)
        # var = 'qcc-Zxxx-r-pWDATA-pp625-ps5000-x-zzwgs84point'
        var = zzwgs84point[0]
        column = self.data.get_column_view(var)[0]
        new_column_lat = []
        new_column_lon = []
        for item in column:
            res = wkt_point_split(item)
            new_column_lat.append(res[1])
            new_column_lon.append(res[0])

        extended_data = self.data.add_column(
            ContinuousVariable('latitude'),
            new_column_lat
        ).add_column(
            ContinuousVariable('longitude'),
            new_column_lon
        )

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


# class OneHotStrings(SharedComputeValue):

#     def __init__(self, fn, new_feature):
#         super().__init__(fn)
#         self.new_feature = new_feature

#     def __eq__(self, other):
#         return self.compute_shared == other.compute_shared \
#             and self.new_feature == other.new_feature

#     def __hash__(self):
#         return hash((self.compute_shared, self.new_feature))

#     def compute(self, data, shared_data):
#         indices = shared_data[self.new_feature]
#         col = np.zeros(len(data))
#         col[indices] = 1
#         return col


if __name__ == "__main__":
    # pylint: disable=ungrouped-imports
    from Orange.widgets.utils.widgetpreview import WidgetPreview  # since Orange 3.20.0
    WidgetPreview(HXLAuto).run()
