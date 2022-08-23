import csv
from Orange.data.io import FileFormat

import logging
log = logging.getLogger(__name__)


class RAWFileReader(FileFormat):
    """Reader for comma separated files"""

    EXTENSIONS = ('.txt', '.raw')
    DESCRIPTION = 'Raw file'
    DELIMITERS = ',;:\t$ '
    SUPPORT_COMPRESSED = False
    SUPPORT_SPARSE_DATA = False
    PRIORITY = 20
    OPTIONAL_TYPE_ANNOTATIONS = True

    def read(self):
        pass

    @classmethod
    def write_file(cls, filename, data, with_annotations=True):

        log.exception('RAWFileReader TODO called')
        log.exception(filename)
        log.exception(data)

        # with cls.open(filename, mode='wt', newline='', encoding='utf-8') as file:
        #     writer = csv.writer(file, delimiter=cls.DELIMITERS[0])
        #     cls.write_headers(writer.writerow, data, with_annotations)
        #     cls.write_data(writer.writerow, data)
        #     cls.write_table_metadata(filename, data)