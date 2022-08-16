
from orangewidget.utils.signals import summarize, PartialSummary
from orangewidget.utils.signals import format_summary_details
from AnyQt.QtCore import Qt


class FileRAW:
    auto_summary = False
    pass


class FileRAWCollection:
    auto_summary = False
    pass


@summarize.register
def summarize_(data: FileRAW):
    return PartialSummary(
        data.approx_len(),
        format_summary_details(data, format=Qt.RichText))


@summarize.register
def summarize_(data: FileRAWCollection):
    return PartialSummary(
        data.approx_len(),
        format_summary_details(data, format=Qt.RichText))
