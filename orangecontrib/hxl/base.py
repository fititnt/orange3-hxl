
from abc import ABC, abstractmethod
from dataclasses import dataclass
import os
from pathlib import Path
from genericpath import exists, isdir, isfile
from re import Pattern
import re
import shutil
from typing import Tuple, Type, Union

import requests

import logging
from orangewidget.utils.signals import summarize, PartialSummary
from Orange.widgets.utils.state_summary import format_summary_details, \
    format_multiple_summaries
from AnyQt.QtCore import Qt
from orangecontrib.hxl.vars import DATAVAULT_BASE, DATAVAULT_TEMP, DATAVAULT_TEMP_SENSITIVE, INFIX_INPUT_RAWFILE, INFIX_INPUT_RAWTEMP, INFIX_INPUT_RAWTRANSFILE, INFIX_INPUT_RAWUNCOMPFILE

from orangecontrib.hxl.widgets.utils import bytes_to_human_readable, file_or_path_raw_metadata, string_to_list

log = logging.getLogger(__name__)


# DATAVAULT_BASE = f'{Path.home()}/.orange3data'
# INFIX_INPUT_RAWFILE = 'rawinput'
# INFIX_INPUT_RAWUNCOMPFILE = 'unzipedinput'  # @TODO rename to rawinputs


# @TODO create some widged only for inspect other raw resources

class DataVault:

    default_data_vault: str = None
    # entrypoint: str = 'rawinput'
    entrypoint: str = INFIX_INPUT_RAWFILE
    unzipedinput: str = INFIX_INPUT_RAWUNCOMPFILE
    # transformedinput: str = 'transformedinput'
    transformedinput: str = INFIX_INPUT_RAWTRANSFILE
    _temp: str = None
    _temp_sensitive: str = None

    def __init__(self):
        # self.default_data_vault = f'{Path.home()}/.orange3data'
        self.default_data_vault = DATAVAULT_BASE
        self._temp = DATAVAULT_TEMP
        self._temp_sensitive = DATAVAULT_TEMP_SENSITIVE

    def initialize(self):
        if not exists(self.default_data_vault):
            os.makedirs(self.default_data_vault)
            os.makedirs(self.default_data_vault + '/' + self.entrypoint)
            os.makedirs(self.default_data_vault + '/' + self.unzipedinput)
            os.makedirs(self.default_data_vault + '/' + self.transformedinput)
            os.makedirs(self.default_data_vault + '/' + self.tempbase)
        if not exists(self._temp):
            os.makedirs(self._temp)
        if not exists(self._temp_sensitive):
            os.makedirs(self._temp_sensitive)

    def is_initialized(self):
        if exists(self.default_data_vault) and exists(self._temp) and \
                exists(self._temp_sensitive):
            return True
        return False

    def download_resource(
        self,
        source_uri: str,
        res_hash: str,
        res_alias: str = None,
        use_cache: bool = True,
        ttl: int = None,
        validator: Type['ValidationCheckResource'] = None
    ) -> Tuple[str, bool, str]:
        if not self.is_initialized():
            raise RuntimeError('Not initialized')

        is_valid = True
        info = ''

        base = self.default_data_vault + '/' + self.entrypoint + '/' + res_hash
        fullname = base + '/' + res_hash
        fullname_temp = self._temp + res_hash
        if not exists(base):
            os.makedirs(base)

        if exists(fullname):
            if use_cache is True:
                log.exception('download_resource already cached')
                return fullname, is_valid, 'Using cache'
            if ttl is not None:
                # @TODO implement this part
                pass
            log.exception('download_resource cache exist, but revalidating...')

        r = requests.get(source_uri, allow_redirects=True)
        # @TODO make checks if source is correct, not error, etc

        if not ValidationCheckResource.is_http_status_code_okay_save(
                r.status_code):
            return None, False, f'Status code not okay {r.status_code}'

        if validator is not None:
            log.exception('download_resource validator...')
            open(fullname_temp, 'wb').write(r.content)
            is_valid, info = validator.file_valid_check(fullname_temp)
            log.exception([is_valid, info])
            if is_valid:
                if exists(fullname):
                    os.remove(fullname)
                shutil.copyfile(fullname_temp, fullname)
        else:
            log.exception('download_resource validator skiped')
            open(fullname, 'wb').write(r.content)

        return fullname, is_valid, info

    @staticmethod
    def resource_path(
        res_group: str = None,
        res_hash: str = None,
        res: Type['ResourceRAW'] = None
    ) -> str:
        # @TODO add something else if we allow user-configuration
        _path = f'{Path.home()}/.orange3data'
        if res is not None:
            if isinstance(res, FileRAW):
                return _path + '/' + res.res_group + '/' + res.res_hash + \
                    '/' + res.res_hash
            if isinstance(res, FileRAWCollection):
                return _path + '/' + res.res_group + '/' + res.res_hash

        return _path + '/' + res_group + '/' + res_hash + '/' + res_hash

    @staticmethod
    def resource_summary(res_group: str, res_hash: str, res_direct: Path = None) -> dict:
        if res_direct and isinstance(res_direct, Path):
            _fullpath = res_direct
        else:
            _fullpath = DataVault.resource_path(res_group, res_hash)
        if os.path.isfile(_fullpath):
            _stat = Path(_fullpath).stat()
            return {
                'files': 1,
                'size': bytes_to_human_readable(_stat.st_size),
                'path': _fullpath
            }
        elif os.path.isdir(_fullpath):
            root_directory = Path(_fullpath)
            _size = 0
            _file_count = 0
            for _item in root_directory.glob('**/*'):
                if _item.is_file():
                    _file_count += 1
                    _size += _item.stat().st_size
            # size = sum(f.stat().st_size for f in root_directory.glob('**/*') if f.is_file())
            # @TODO
            return {
                'files': _file_count,
                'size':  bytes_to_human_readable(_size),
                'path': _fullpath
            }
        else:
            return None
            # error
            # return {
            #     'files': -1,
            #     'size': -1,
            #     'path': _fullpath
            # }

    @staticmethod
    def resource_detail(res: Type['ResourceRAW']) -> dict:
        if not res:
            return None

        if res.res_direct:
            _fullpath = res.res_direct
        else:
            # _fullpath = DataVault.resource_path(res.res_group, res.res_hash)
            _fullpath = DataVault.resource_path(res=res)

        # return {'todo3': _fullpath}

        return file_or_path_raw_metadata(_fullpath)


class ResourceRAW(ABC):
    res_hash: str = None
    res_group: str = None
    res_alias: str = 'unnamed'
    res_direct: str = None  # use case: file inside unziped resource
    # Not implemented
    disk_encrypted: bool = False

    @abstractmethod
    def base(self):
        pass

    @abstractmethod
    def ready(self):
        pass

    def __str__(self):
        return f'<{self.__class__.__name__}(res_hash={str(self.res_hash)}' + \
            f' ,res_group={str(self.res_group)})>'

    def set_resource(self, res_hash: str, res_group: str, res_alias: str = None):
        self.res_hash = res_hash
        self.res_group = res_group
        if res_alias and len(res_alias) > 0:
            self.res_alias = res_alias

    @abstractmethod
    def ready(self):
        pass

    def urn(self) -> str:
        if self.res_direct:
            return 'urn:data:' + str(self.res_direct)
        elif self.res_hash:
            return 'urn:data:' + self.res_group + ':' + self.res_hash
        else:
            return 'urn:data:void:void'


class FileRAW(ResourceRAW):
    res_group = INFIX_INPUT_RAWFILE

    def base(self) -> str:
        # return DATAVAULT_BASE + '/rawinput/' + self.res_hash + self.res_hash
        if self.res_direct:
            return f'{DATAVAULT_BASE}/{str(self.res_direct)}'
        else:
            return f'{DATAVAULT_BASE}/rawinput/{self.res_hash}/{self.res_hash}'

    # def urn(self) -> str:
    #     if self.res_direct:
    #         return 'urn:data:' + self.res_direct
    #     else:
    #         return 'urn:data:' + self.res_group + ':' + self.res_hash

    def set_direct(self, res_direct: str):
        self.res_group = '_direct_'
        # self.res_direct = str(res_direct)
        self.res_direct = res_direct
        return self

    def ready(self):
        if not self.res_hash or not self.res_group:
            return None
        return DataVault.resource_summary(
            self.res_group, self.res_hash, self.res_direct)


class FileRAWCollection(ResourceRAW):
    res_group = INFIX_INPUT_RAWUNCOMPFILE

    def already_ready(self):
        # @TODO actually try check if something change on source
        return self.ready()

    def base(self) -> str:
        return f'{DATAVAULT_BASE}/unzipedinput/{self.res_hash}'

    def ready(self):
        # if self.res_direct is None and (not self.res_hash or not self.res_group):
        #     return None

        if exists(self.base()):
            return True

        return DataVault.resource_summary(
            self.res_group, self.res_hash)

    # def select(self, extensions: list = None, filename_or_pattern: Union[Pattern, str] = None):
    def select(
        self,
        extensions: list = None,
        subdirectory: list = None,
        filename_list: list = None,
        filename_pattern: str = None
    ):
        parameters: str = '**/*'
        root_directory = Path(self.base())

        # @TODO implement subdirectory option

        # # for _item in root_directory.glob('**/*'):
        # # log.exception(f' select[{extensions}] [{str(filename_or_pattern)})]')

        # # if re.search("^API_8_DS2_en_csv_v2_4357272.csv$", "metadata_indicator_api_8_ds2_en_csv_v2_4357272.csv", re.IGNORECASE):
        # if re.search("^API_8_DS2_en_csv_v2_4357272\.csv$", "metadata_indicator_api_8_ds2_en_csv_v2_4357272.csv", re.IGNORECASE):
        #     log.exception(f' exact certoww]')
        # else:
        #     log.exception(f' exact err]')
        # if re.search("^API", "API_8_DS2_en_csv_v2_4357272.csv", re.IGNORECASE):
        #     log.exception(f' foi]')
        # else:
        #     log.exception(f' nao foi]')
        # # testss=re.search("^API", "API_8_DS2_en_csv_v2_4357272.csv", re.IGNORECASE)
        # # log.exception(f' ssss[{str(testss)})]')
        # # testss=re.search("^API", "AxPI_8_DS2_en_csv_v2_4357272.csv", re.IGNORECASE)
        # # log.exception(f' sxxsss[{str(testss)})]')
        # # log.exception(f' filename_or_pattern[{str(filename_or_pattern)})]')
        # # testss2=re.search(filename_or_pattern, "API_8_DS2_en_csv_v2_4357272.csv", re.IGNORECASE)
        # # log.exception(f' testss2[{str(testss2)})]')

        # if filename_or_pattern:
        #     _pattern = re.compile(filename_or_pattern, re.IGNORECASE)
        #     _search_filename = filename_or_pattern.lower()

        # if filename_or_pattern:
        #     if isinstance(filename_or_pattern, Pattern):
        #         _pattern = filename_or_pattern
        #         _search_filename = None
        #     else:
        #         _pattern = re.compile(filename_or_pattern, re.IGNORECASE)
        #         _search_filename = filename_or_pattern.lower()
        # if filename_pattern

        success_exact = []
        success_pattern = []
        less_restricted = []
        for _item in root_directory.glob(parameters):
            # log.exception(f' testing [{str(_item)})]')
            if _item.is_file():
                selected_path = _item.relative_to(DATAVAULT_BASE)
                filename_now = _item.name

                if extensions:
                    _okay = False
                    for _ext in extensions:
                        if filename_now.endswith(_ext):
                            _okay = True
                            break
                    if not _okay:
                        continue

                if subdirectory:
                    _okay = False
                    for _subdir in subdirectory:
                        if str(selected_path).startswith(_subdir):
                            _okay = True
                            break
                    if not _okay:
                        continue
                if filename_list and filename_now in filename_list:
                    # success_exact.append(_item)
                    success_exact.append(selected_path)
                if filename_pattern and \
                        re.search(filename_pattern,
                                  filename_now, re.IGNORECASE):
                    # success_pattern.append(_item)
                    success_pattern.append(selected_path)

                if not filename_list and not filename_pattern:
                    # less_restricted.append(_item)
                    less_restricted.append(selected_path)

        if len(success_exact) > 0:
            sorted(success_exact)
            _result = success_exact[0]
        elif len(success_pattern) > 0:
            sorted(success_pattern)
            _result = success_pattern[0]
        elif len(less_restricted) > 0:
            sorted(less_restricted)
            _result = less_restricted[0]
        else:
            return None

        # @TODO implement a sorting order of "just get the big file" instead
        #       name ordering

        _file_raw = FileRAW()
        _file_raw.res_hash = self.res_hash
        _file_raw.set_direct(_result)

        # log.exception(f' final result [{str(_result)})]')
        return _file_raw
        return None


class ValidationCheckResource:
    """Dataclass to envelope valid checks to check downloaded resources

    It's quite rudimentar, but can work for early checks to abort operations
    """
    _res_valid_mimetypes: list = None
    _res_valid_havestring: list = None
    _res_valid_nothavestring: list = None

    # def __init__(
    #     self,
    #     res_valid_mimetypes: Union[list, str],
    #     res_valid_havestring: Union[list, str],
    #     res_valid_nothavestring: Union[list, str],
    # ) -> None:
    #     if res_valid_mimetypes:
    #         self.res_valid_mimetypes = res_valid_mimetypes
    #         # if isinstance(res_valid_mimetypes, str):
    #         #     res_valid_mimetypes = string_to_list(res_valid_mimetypes, '|')
    #         # self.res_valid_mimetypes = res_valid_mimetypes

    #     if res_valid_havestring:
    #         # if isinstance(res_valid_havestring, str):
    #         #     res_valid_havestring = string_to_list(
    #         #         res_valid_havestring, '|')
    #         self.res_valid_havestring = res_valid_havestring

    #     if res_valid_nothavestring:
    #         # if isinstance(res_valid_nothavestring, str):
    #         #     res_valid_nothavestring = string_to_list(
    #         #         res_valid_nothavestring, '|')
    #         self.res_valid_nothavestring = res_valid_nothavestring

    @property
    def res_valid_mimetypes(self):
        return self._res_valid_mimetypes

    @res_valid_mimetypes.setter
    def res_valid_mimetypes(self, value: Union[list, str]) -> None:
        if isinstance(value, str):
            value = string_to_list(value, '|')
        self._res_valid_mimetypes = value

    @property
    def res_valid_havestring(self):
        return self._res_valid_havestring

    @res_valid_havestring.setter
    def res_valid_havestring(self, value: Union[list, str]) -> None:
        if isinstance(value, str):
            value = string_to_list(value, '|')
        self._res_valid_havestring = value

    @property
    def res_valid_nothavestring(self):
        return self._res_valid_nothavestring

    @res_valid_nothavestring.setter
    def res_valid_nothavestring(self, value: Union[list, str]) -> None:
        if isinstance(value, str):
            value = string_to_list(value, '|')
        self._res_valid_nothavestring = value

    def file_valid_check(
        self,
        file_path: str
    ) -> Tuple[bool, str]:

        is_valid = False
        is_valid_havetext = None
        is_valid_nothavetext = None
        is_valid_mimetype = None
        info = []

        mimetypes = self.res_valid_mimetypes
        havetext = self.res_valid_havestring
        nothavetext = self.res_valid_nothavestring

        # Abort early for obvious wrong fail.
        if not Path(file_path).is_file():
            return False, "File not exist on disk"

        if mimetypes is not None:
            try:
                import magic
                has_magic = True
            except ImportError:
                has_magic = False

            if has_magic:
                _filemime = magic.from_file(file_path, mime=True)
                if _filemime not in mimetypes:
                    is_valid_mimetype = False
                    info.append(f'Mime type [{_filemime}] not match')
            else:
                info.append('magic not installed. ignoring mime type check')

        if havetext is not None or nothavetext is not None:
            sample = False
            try:
                with open(file_path, "r") as f:
                    sample = f.read(16384)
            except UnicodeDecodeError:
                pass  # Fond non-text data

            if sample is False or len(sample) == 0:
                is_valid = False
                info.append(f'File is either empty or is binary')
                return is_valid, is_valid, '; '.join(info)

        if havetext is not None:
            is_valid_havetext = False
            for item in havetext:
                if sample.find(item) > -1:
                    is_valid_havetext = True
                    break
            if is_valid_havetext is False:
                info.append(f'File does not have any of havetext checks')
        if nothavetext is not None:
            is_valid_nothavetext = True
            for item in nothavetext:
                if not sample.find(item) == -1:
                    is_valid_nothavetext = False
                    info.append(f'File contains {item} of nothavetext')
                    break

        if is_valid_mimetype is not False and \
            is_valid_havetext is not False and \
                is_valid_nothavetext is not False:
            is_valid = True

        return is_valid, '; '.join(info)

    @staticmethod
    def is_http_status_code_okay_save(code: int):
        return code in [200]

    # def is_http_status_code_okay_save(self, code: int):
    #     return code in [200]


def format_summary_details_hxl(data):
    if not data or not data.res_group or not data.res_hash:
        return 'None'

    #_fullpath = DataVault.resource_path(data.res_group, data.res_hash)
    _res_summary = DataVault.resource_summary(
        data.res_group, data.res_hash, data.res_direct)
    info = [
        f'Alias: <b>{data.res_alias}</b>'
        # f'Path: <b>{_fullpath}</b><br/>'
    ]
    if _res_summary:
        for key, value in _res_summary.items():
            info.append(f'{key}: <b>{value}</b>')

    return '<br/>'.join(info)

# @summarize.register
# def summarize_(data: FileRAW):
#     return PartialSummary(
#         data.approx_len(),
#         format_summary_details(data, format=Qt.RichText))

# @summarize.register
# def summarize_(data: FileRAW):
#     return PartialSummary(
#         data.res_hash,
#         format_summary_details(data, format=Qt.RichText))


@summarize.register
def summarize_(data: FileRAW):
    return PartialSummary(
        data.urn(),
        format_summary_details_hxl(data))


@summarize.register
def summarize_(data: FileRAWCollection):
    return PartialSummary(
        data.urn(),
        format_summary_details_hxl(data))


# from Orange.widgets.data.owfile import OWFile
# # from Orange.widgets.widget import OWWidget, Input, Output, Msg
# from Orange.widgets.widget import Input


# class PatchWOFileInputs:
#     fileraw = Input(
#         "FileRAW", FileRAW)

# # @Inputs.fileraw
# def set_fileraw(self, fileraw):
#     """set_fileraw"""
#     #log.exception(f'unzipfile set_fileraw [{str(fileraw)}]')
#     if fileraw:
#         self.fileraw = fileraw
#         self.commit()
#     else:
#         self.fileraw = None

# OWFile.Inputs = PatchWOFileInputs
# # OWFile.set_fileraw = set_fileraw

# OWFile.fileraw.__setattr__ = set_fileraw

# OWFilePatched = OWFile

# class OWFilePatched(OWFile):
#     class Inputs:
#         """Inputs"""
#         # specify the name of the input and the type
#         # data = Input("Data", Table)
#         # data = Input("FileRAWCollection", FileRAWCollection)
#         fileraw = Input(
#             "FileRAW", FileRAW)
#         filerawcollection = Input(
#             "FileRAWCollection", FileRAWCollection)
