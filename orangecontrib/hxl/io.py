import csv
import os
from pathlib import Path
import shutil
from Orange.data.io import FileFormat

import logging

from orangecontrib.hxl.base import FileRAW, ResourceRAW
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


def raw_resource_export(res: ResourceRAW, export_path: str):
    log.exception(['raw_resource_export called', res.base(), export_path])
    # log.exception(res)
    # log.exception(export_path)
    if not res:
        return None
    if not isinstance(res, FileRAW):
        raise NotImplementedError('@TODO')

    source_path = res.base()
    if not Path(source_path).exists():
        raise IOError(f'{source_path} not exists')

    if not Path(source_path).is_file():
        raise NotImplementedError(f'{source_path} is not a file')

    def _copy(source: str, target: str):
        return shutil.copyfile(source, target)
        # pass

    def _override(source: str, target: str):
        os.remove(target)
        return _copy(source, target)
        # pass

    source_size = Path(source_path).stat().st_size
    if Path(export_path).is_file():
        export_size = Path(export_path).stat().st_size
        # export_size = Path(export_path).stat().
        if source_size == export_size:
            # @TODO implement cheap memory efficient test to check
            #       files with same size have same hash
            pass
        else:
            log.exception('raw_resource_export _override')
            return _override(source_path, export_path)
    else:
        log.exception('raw_resource_export _copy')
        return _copy(source_path, export_path)
