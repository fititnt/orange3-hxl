import os.path
import logging
from Orange.data.table import Table
from Orange.data.io import \
    TabReader, CSVReader, PickleReader, ExcelReader, XlsReader, FileFormat
from Orange.widgets import gui, widget
from Orange.widgets.widget import Input
from Orange.widgets.settings import Setting
from Orange.widgets.utils.save.owsavebase import OWSaveBase
from Orange.widgets.utils.widgetpreview import WidgetPreview

from orangecontrib.hxl.base import FileRAW
from orangecontrib.hxl.io import RAWFileReader, raw_resource_export

_userhome = os.path.expanduser(f"~{os.sep}")

log = logging.getLogger(__name__)


class HXLRAWSave(OWSaveBase):
    name = "Raw Save"
    description = """
    [WORKING DRAFT] Export a FileRAW outside the internal DataVault
    """
    # icon = "icons/Save.svg"
    # category = "Data"
    # keywords = ["export"]

    icon = "icons/mywidget.svg"
    priority = 67  # where in the widget order it will appear
    category = "Orange3-HXLvisualETL"
    keywords = ["widget", "data", "save", "export", "raw"]

    # settings_version = 3

    class Inputs:
        # data = Input("Data", Table)
        fileraw = Input("FileRAW", FileRAW)

    class Error(OWSaveBase.Error):
        unsupported_sparse = widget.Msg("Use Pickle format for sparse data.")

    add_type_annotations = Setting(True)

    builtin_order = [RAWFileReader, TabReader, CSVReader,
                     PickleReader, ExcelReader, XlsReader]
    builtin_order = [RAWFileReader]

    def __init__(self):
        super().__init__(2)
        # self.grid.addWidget(
        #     gui.checkBox(
        #         None, self, "add_type_annotations",
        #         "Add type annotations to header",
        #         tooltip="Some formats (Tab-delimited, Comma-separated) can include \n"
        #         "additional information about variables types in header rows.",
        #         callback=self.update_messages),
        #     0, 0, 1, 2)
        # self.grid.setRowMinimumHeight(1, 8)
        # self.adjustSize()

    @classmethod
    def get_filters(cls):
        writers = [format for format in FileFormat.formats
                   if getattr(format, 'write_file', None)
                   and getattr(format, "EXTENSIONS", None)]
        writers.sort(key=lambda writer: cls.builtin_order.index(writer)
                     if writer in cls.builtin_order else 99)

        log.exception(['get_filters TODO called', writers])

        writers = [RAWFileReader]

        return {
            **{f"{w.DESCRIPTION} (*{w.EXTENSIONS[0]})": w
               for w in writers},
            **{f"Compressed {w.DESCRIPTION} (*{w.EXTENSIONS[0]}.gz)": w
               for w in writers if w.SUPPORT_COMPRESSED}
        }

    # @Inputs.data
    # def dataset(self, data):
    #     self.data = data
    #     self.on_new_input()

    @Inputs.fileraw
    def set_fileraw(self, fileraw):
        """set_fileraw"""
        if fileraw:
            self.fileraw = fileraw
            # self.commit()
            self.do_save()

            # @TODO only try again this if input changed
            # inputraw = file_raw_info(self.fileraw.base())
            # self.peakraw.setPlainText(inputraw)
        else:
            self.fileraw = None

    def do_save(self):
        # log.exception(['do_save TODO called', self.fileraw, self.filename])

        return raw_resource_export(res=self.fileraw, export_path=self.filename)

    def update_messages(self):
        return None
        super().update_messages()
        self.Error.unsupported_sparse(
            shown=self.data is not None and self.data.is_sparse()
            and self.filename
            and self.writer is not None and not self.writer.SUPPORT_SPARSE_DATA)

    def send_report(self):
        self.report_data_brief(self.data)
        writer = self.writer
        noyes = ["No", "Yes"]
        self.report_items((
            ("File name", self.filename or "not set"),
            ("Format", writer and writer.DESCRIPTION),
            ("Type annotations",
             writer and writer.OPTIONAL_TYPE_ANNOTATIONS
             and noyes[self.add_type_annotations])
        ))

    # def do_save(self):
    #     """
    #     Do the saving.

    #     Default implementation calls the write method of the writer
    #     corresponding to the current filter. This requires that get_filters()
    #     returns is a dictionary whose keys are classes.

    #     Derived classes may simplify this by providing a list of filters and
    #     override do_save. This is particularly handy if the widget supports only
    #     a single format.
    #     """
    #     # This method is separated out because it will usually be overriden
    #     if self.writer is None:
    #         self.Error.unsupported_format(self.filter)
    #         return

    #     log.exception('do_save TODO called')
    #     log.exception(self.filename)
    #     log.exception(self.data)
    #     log.exception(self.fileraw)
    #     self.writer.write(self.filename, self.data)
    # # @classmethod
    # def migrate_settings(cls, settings, version=0):
    #     def migrate_to_version_2():
    #         # Set the default; change later if possible
    #         settings.pop("compression", None)
    #         settings["filter"] = next(iter(cls.get_filters()))
    #         filetype = settings.pop("filetype", None)
    #         if filetype is None:
    #             return

    #         ext = cls._extension_from_filter(filetype)
    #         if settings.pop("compress", False):
    #             for afilter in cls.get_filters():
    #                 if ext + ".gz" in afilter:
    #                     settings["filter"] = afilter
    #                     return
    #             # If not found, uncompressed may have been erroneously set
    #             # for a writer that didn't support if (such as .xlsx), so
    #             # fall through to uncompressed
    #         for afilter in cls.get_filters():
    #             if ext in afilter:
    #                 settings["filter"] = afilter
    #                 return

    #     if version < 2:
    #         migrate_to_version_2()

    #     if version < 3:
    #         if settings.get("add_type_annotations") and \
    #                 settings.get("stored_name") and \
    #                 os.path.splitext(settings["stored_name"])[1] == ".xlsx":
    #             settings["add_type_annotations"] = False

    def initial_start_dir(self):
        if self.filename and os.path.exists(os.path.split(self.filename)[0]):
            return self.filename
        else:
            data_name = getattr(self.data, 'name', '')
            if data_name:
                if self.writer is None:
                    self.filter = self.default_filter()
                assert self.writer is not None
                data_name += self.writer.EXTENSIONS[0]
            return os.path.join(self.last_dir or _userhome, data_name)

    def valid_filters(self):
        if self.data is None or not self.data.is_sparse():
            return self.get_filters()
        else:
            return {filt: writer for filt, writer in self.get_filters().items()
                    if writer.SUPPORT_SPARSE_DATA}

    def default_valid_filter(self):
        valid = self.valid_filters()
        if self.data is None or not self.data.is_sparse() \
                or (self.filter in valid
                    and valid[self.filter].SUPPORT_SPARSE_DATA):
            return self.filter
        return next(iter(valid))


if __name__ == "__main__":  # pragma: no cover
    WidgetPreview(HXLRAWSave).run(Table("iris"))
