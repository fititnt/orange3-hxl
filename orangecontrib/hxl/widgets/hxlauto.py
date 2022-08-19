"""hxlauto"""

import json
import logging
import numpy as np
# from Orange.data import Table
from Orange.widgets import gui
from Orange.widgets.settings import Setting
from Orange.widgets.widget import OWWidget, Input, Output, Msg
# from Orange.data import Table, Domain, DiscreteVariable, StringVariable
from Orange.data import Table, Domain, DiscreteVariable, ContinuousVariable, StringVariable
from Orange.data.util import SharedComputeValue, get_unique_names

from orangecontrib.hxl.widgets.utils import WKTPointSplit, orange_data_names_normalization, orange_data_roles_ex_hxl, string_to_list, wkt_point_split

# from .utils import *

log = logging.getLogger(__name__)


class HXLAuto(OWWidget):
    """HXL Statistical Role"""
    # Widget needs a name, or it is considered an abstract widget
    # and not shown in the menu.
    name = "Statistical Role"
    # id = "orange.widgets.data.info"
    description = """
    Change statistical role (the "feature", "target", "meta", "ignore")
    using HXL patterns instead of stric exact names for the data variables.
    """
    icon = "icons/mywidget.svg"
    priority = 130  # where in the widget order it will appear
    category = "Orange3-HXLvisualETL"
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

        self.hxl_h_meta = '#meta|#date|#status'
        self.hxlh_meta_box = gui.lineEdit(
            self.controlArea, self, "hxl_h_meta", box="Base hashtags: Role=meta")

        self.hxl_a_meta = '+code|+codicem|+id|+name'
        self.hxl_a_meta_box = gui.lineEdit(
            self.controlArea, self, "hxl_a_meta", box="HXL attributes: Role=meta")

        gui.separator(self.controlArea)
        self.hxl_h_ignore = ''
        self.hxl_h_ignore_box = gui.lineEdit(
            self.controlArea, self, "hxl_h_ignore", box="Base hashtags: Role=ignore")

        self.hxl_a_ignore = ''
        self.hxl_a_ignore_box = gui.lineEdit(
            self.controlArea, self, "hxl_a_ignore", box="HXL attributes: Role=ignore")

        box = gui.widgetBox(self.controlArea, "Info")
        self.infoa = gui.widgetLabel(
            box, "No data on input yet, waiting to get something."
        )
        self.infob = gui.widgetLabel(box, "")

        gui.separator(self.controlArea)
        self.optionsBox = gui.widgetBox(self.controlArea, "Options")

        # @TODO implement some way to enforce weight
        #       https://orange3.readthedocs.io/projects/orange-data-mining-library/en/latest/reference/data.instance.html?highlight=weight#Orange.data.Instance.weight
        # gui.spin(
        #     self.optionsBox,
        #     self,
        #     "proportion",
        #     minv=10,
        #     maxv=90,
        #     step=10,
        #     label="Sample Size [%]:",
        #     callback=[self.selection, self.checkCommit],
        # )
        # gui.checkBox(
        #     self.optionsBox, self, "commitOnChange", "Commit data on selection change"
        # )
        gui.button(self.optionsBox, self, "Commit", callback=self.commit)
        self.optionsBox.setDisabled(False)

    @Inputs.data
    def set_data(self, data):
        """set_data"""
        if data:
            self.data = data
        else:
            self.data = None

    def commit(self):
        """commit"""
        if not self.data:
            self.infoa.setText("No input data yet")
            return None
        # else:
        #     self.infoa.setText("Processing data...")
        #     self.optionsBox.setDisabled(False)
        # log.debug("commit: %s", self.data)

        # hxl_h_meta = None
        hxl_h_meta = string_to_list(self.hxl_h_meta, None, None, '#')
        hxl_a_meta = string_to_list(self.hxl_a_meta, None, None, '+')
        hxl_h_ignore = string_to_list(self.hxl_h_ignore, None, None, '#')
        hxl_a_ignore = string_to_list(self.hxl_a_ignore, None, None, '+')
        # if self.hxlh_meta:
        #     _temp = filter(None, map(str.strip, self.hxl_h_meta.split(',')))
        #     hxl_h_meta = _temp if len(_temp) > 0 else None
        # hxla_meta = None
        # if self.hxla_meta:
        #     _temp = filter(None, map(str.strip, self.hxla_meta.split(',')))
        #     hxla_meta = _temp if len(_temp) > 0 else None

        # @TODO make this part not hardcoded

        # log.exception('self.data.domain.variables')
        # log.exception(self.data.domain.variables)

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

        # log.exception('zzwgs84point 0')
        # log.exception(zzwgs84point)

        # Either not have Point(12.34 56.78) or already processed
        if len(zzwgs84point) == 0 or already_have_latlon:

            # log.exception(f'>>> (pre) orange_data_roles_ex_hxl')
            extended_data_3, _changes = orange_data_names_normalization(
                self.data)
            extended_data_2, _changes2 = orange_data_roles_ex_hxl(
                extended_data_3,
                hxl_h_meta=hxl_h_meta,
                hxl_a_meta=hxl_a_meta,
                hxl_h_ignore=hxl_h_ignore,
                hxl_a_ignore=hxl_a_ignore,
            )

            if _changes2:
                self.infoa.setText(json.dumps(
                    _changes2, indent=4, sort_keys=True, ensure_ascii=False))
            # self.Outputs.data.send(self.data)
            self.Outputs.data.send(extended_data_2)
            return None

        if len(zzwgs84point) > 1:
            log.exception(
                "@TODO not implemented yet with more than one zzwgs84point")
            # return None

        # log.exception('var_names')
        # log.exception(var_names)
        # log.exception('zzwgs84point')
        # log.exception(zzwgs84point)
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
        # self.Outputs.data.send(extended_data)
        # log.exception(f'>>> (pre) orange_data_roles_ex_hxl')
        # extended_data_3, _changes = orange_data_names_normalization(self.data)
        extended_data_3, _changes = orange_data_names_normalization(
            extended_data)
        extended_data_2, _changes2 = orange_data_roles_ex_hxl(extended_data_3)

        if _changes2:
            self.infoa.setText(json.dumps(
                _changes2, indent=4, sort_keys=True, ensure_ascii=False))
        self.Outputs.data.send(extended_data_2)
        # self.Outputs.data.send(extended_data)
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


if __name__ == "__main__":
    # pylint: disable=ungrouped-imports
    from Orange.widgets.utils.widgetpreview import WidgetPreview  # since Orange 3.20.0
    WidgetPreview(HXLAuto).run()
