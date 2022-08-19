"""HXLShortNames
"""

import logging

# from Orange.data import Table
from Orange.widgets import gui
from Orange.widgets.settings import Setting
from Orange.widgets.widget import OWWidget, Input, Output, Msg

# from Orange.data import Table, Domain, DiscreteVariable, StringVariable
from Orange.data import Table, Domain

from orangecontrib.hxl.widgets.utils import bcp47_shortest_name, sortname

log = logging.getLogger(__name__)


class HXLShortNames(OWWidget):
    """HXLShortNames"""
    # Widget needs a name, or it is considered an abstract widget
    # and not shown in the menu.
    name = "HXL short names"
    description = """
    [EARLY DRAFT] Make HXLated input data with shorter variable names.
    """
    icon = "icons/mywidget.svg"
    priority = 9995  # where in the widget order it will appear
    category = "Orange3-HXLvisualETL"
    keywords = ["widget", "data"]
    want_main_area = False
    resizing_enabled = False

    label = Setting("")
    auto_apply = Setting(True)

    class Inputs:
        """Inputs"""
        # specify the name of the input and the type
        data = Input("Data", Table)

    class Outputs:
        """Outputs"""
        # if there are two or more outputs, default=True marks the default output
        data = Output("Data", Table, default=True)

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
    def set_data(self, data):  # pylint: disable=missing-function-docstring
        if data:
            self.data = data
        else:
            self.data = None

    def commit(self):  # pylint: disable=missing-function-docstring
        new_domain = []

        # @TODO make early check if have input data before continue

        # log.exception(' >>>> self.data.domain.attributes')
        # log.exception(type(self.data.domain.attributes))
        # log.exception(self.data.domain.attributes)
        # log.exception(' >>>> self.data.domain.class_vars')
        # log.exception(type(self.data.domain.class_vars))
        # log.exception(self.data.domain.class_vars)
        # log.exception(' >>>> self.data.domain.metas')
        # log.exception(type(self.data.domain.metas))
        # log.exception(self.data.domain.metas)

        new_attributes = []
        history_new_names = []
        for item in self.data.domain.attributes:
            # item = item.renamed(bcp47_shortest_name(item.name))
            new_name = sortname(item.name, history_new_names)
            # log.exception(new_name)
            history_new_names.append(new_name)
            item = item.renamed(new_name)
            # log.exception(type(self.data.domain.attributes))
            new_attributes.append(item)

        new_metas = []
        for item in self.data.domain.metas:
            new_name = sortname(item.name, history_new_names)
            # log.exception(new_name)
            history_new_names.append(new_name)
            item = item.renamed(new_name)
            new_metas.append(item)

        new_class_vars = []
        for item in self.data.domain.class_vars:
            # item = item.renamed(bcp47_shortest_name(item.name))
            new_name = sortname(item.name, history_new_names)
            # log.exception(new_name)
            history_new_names.append(new_name)
            item = item.renamed(new_name)
            new_class_vars.append(item)

        new_domain = Domain(
            # self.data.domain.attributes,
            new_attributes,
            # self.data.domain.class_vars, self.data.domain.metas
            new_class_vars, new_metas
        )
        extended_data = self.data.transform(new_domain)

        # log.exception('self.data.domain')
        # log.exception(self.data.domain)
        # log.exception('new_domain')
        # log.exception(new_domain)
        # log.exception('extended_data')
        # log.exception(extended_data)
        # log.exception(type(self.data.domain))

        # @TODO why the variable is renamed here, but not on interface? Humm...
        # self.apply.now()
        self.Outputs.data.send(extended_data)

        # self.Outputs.data.send(self.data)

    def send_report(self):
        """send_report"""
        # self.report_plot() includes visualizations in the report
        self.report_caption(self.label)


if __name__ == "__main__":
    # pylint: disable=ungrouped-imports
    from Orange.widgets.utils.widgetpreview import WidgetPreview  # since Orange 3.20.0
    WidgetPreview(HXLShortNames).run()
