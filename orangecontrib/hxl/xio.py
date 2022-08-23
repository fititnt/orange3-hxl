# ==============================================================================
#
#          FILE: xio.py
#                orangecontrib/hxl/xio.py
#
#         USAGE:  It's a python library
#
#   DESCRIPTION:  I/O related utils. Renamed from io.py to xio.py to make
#                 python3 -m doctest happy.
#
#       OPTIONS:  ---
#
#  REQUIREMENTS:  ---
#          BUGS:  ---
#         NOTES:  ---
#       AUTHORS:  Emerson Rocha <rocha[at]ieee.org>
# COLLABORATORS:  ---
#       COMPANY:  EticaAI
#       LICENSE:  Public Domain dedication or Zero-Clause BSD
#                 SPDX-License-Identifier: Unlicense OR 0BSD
#       VERSION:  v1.0.0
#       CREATED:  2022-08-23 18:47 UTC
#      REVISION:  ---
# ==============================================================================
"""Common library for 999999999_*.py cli scripts
"""
# pytest
#    python3 -m doctest ./orangecontrib/hxl/xio.py

import csv
import os
from pathlib import Path
import shutil
import requests
from Orange.data.io import FileFormat

import logging

from orangecontrib.hxl.base import FileRAW, ResourceRAW
log = logging.getLogger(__name__)


class RAWFileReader(FileFormat):
    """Reader for RAW"""

    # EXTENSIONS = ('.raw', '.csv', '.tsv', '.xlsx')
    # EXTENSIONS = ('*.*')
    EXTENSIONS = ('.raw')
    DESCRIPTION = 'Raw file'
    DELIMITERS = ',;:\t$ '
    SUPPORT_COMPRESSED = False
    SUPPORT_SPARSE_DATA = False
    PRIORITY = 1
    OPTIONAL_TYPE_ANNOTATIONS = False

    def read(self):
        pass

    @classmethod
    def write_file(cls, filename, data, with_annotations=True):
        raise DeprecationWarning('Use raw_resource_export')


def raw_resource_export(res: ResourceRAW, export_path: str):
    """raw_resource_export export resource on internal DataVault

    Args:
        res (ResourceRAW): _description_
        export_path (str): _description_

    Raises:
        NotImplementedError: _description_
        IOError: _description_
        NotImplementedError: _description_

    Returns:
        _type_: _description_
    """
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


def http_request_head(uri: str) -> dict:
    """
    >>> http_request_head("https://api.worldbank.org/v2/en/topic/8?downloadformat=csv")
    """
    result = {
        'code': None,
        'headers': None
    }
    response = requests.head(uri)

    result['code'] = response.status_code
    result['headers'] = response.headers
    # print('tst')
    return response, result
