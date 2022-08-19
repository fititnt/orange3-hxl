
from abc import ABC, abstractmethod
import os
from pathlib import Path
from genericpath import exists, isdir, isfile

import requests

import logging
from orangewidget.utils.signals import summarize, PartialSummary
from Orange.widgets.utils.state_summary import format_summary_details, \
    format_multiple_summaries
from AnyQt.QtCore import Qt

from orangecontrib.hxl.widgets.utils import bytes_to_human_readable

log = logging.getLogger(__name__)


VALT_BASE = f'{Path.home()}/.orange3data'
ETL_RAW_FILE = 'rawinput'
ETL_RAW_FILES = 'unzipedinput'  # @TODO rename to rawinputs


# @TODO create some widged only for inspect other raw resources

class DataVault:

    default_data_vault: str = None
    entrypoint: str = 'rawinput'
    unzipedinput: str = ETL_RAW_FILES
    transformedinput: str = 'transformedinput'

    def __init__(self):
        self.default_data_vault = f'{Path.home()}/.orange3data'

    def initialize(self):
        if not exists(self.default_data_vault):
            os.makedirs(self.default_data_vault)
            os.makedirs(self.default_data_vault + '/' + self.entrypoint)
            os.makedirs(self.default_data_vault + '/' + ETL_RAW_FILES)
            os.makedirs(self.default_data_vault + '/' + self.transformedinput)

    def is_initialized(self):
        return exists(self.default_data_vault)

    def download_resource(
        self,
        source_uri: str,
        res_hash: str,
        res_alias: str = None,
        force: bool = False
    ):
        if not self.is_initialized():
            raise RuntimeError('Not initialized')

        base = self.default_data_vault + '/' + self.entrypoint + '/' + res_hash
        fullname = base + '/' + res_hash
        if not exists(base):
            os.makedirs(base)

        if exists(fullname) and force is not True:
            return fullname
        r = requests.get(source_uri, allow_redirects=True)
        # @TODO make checks if source is correct, not error, etc

        open(fullname, 'wb').write(r.content)

        return fullname

    @staticmethod
    def resource_path(res_group: str, res_hash: str) -> str:
        # @TODO add something else if we allow user-configuration
        _path = f'{Path.home()}/.orange3data'
        return _path + '/' + res_group + '/' + res_hash + '/' + res_hash

    @staticmethod
    def resource_summary(res_group: str, res_hash: str, res_direct: Path = None) -> str:
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
    res_group = ETL_RAW_FILE

    def base(self) -> str:
        # return VALT_BASE + '/rawinput/' + self.res_hash + self.res_hash
        if self.res_direct:
            return f'{VALT_BASE}/{str(self.res_direct)}'
        else:
            return f'{VALT_BASE}/rawinput/{self.res_hash}/{self.res_hash}'

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
    res_group = ETL_RAW_FILES

    def already_ready(self):
        # @TODO actually try check if something change on source
        return self.ready()

    def base(self) -> str:
        return f'{VALT_BASE}/unzipedinput/{self.res_hash}'

    def ready(self):
        # if self.res_direct is None and (not self.res_hash or not self.res_group):
        #     return None

        if exists(self.base()):
            return True

        return DataVault.resource_summary(
            self.res_group, self.res_hash)

    def select(self, extensions: list = None, filenames: list = None):
        parameters: str = '**/*'
        root_directory = Path(self.base())
        # for _item in root_directory.glob('**/*'):
        log.exception(f' [{extensions}] [{filenames}]')
        for _item in root_directory.glob(parameters):
            if _item.is_file():
                okay = None
                filenamewithext = _item.name.lower()
                if extensions:
                    for _ext in extensions:
                        if filenamewithext.lower().endswith(_ext):
                            okay = True
                            break
                    if okay is not True:
                        break
                if filenames:
                    for _searchname in filenames:
                        _searchname2 = _searchname.replace('*', '').lower()
                        if filenamewithext.find(_searchname2) > -1:
                            okay = True
                    if okay is not True:
                        break
                    # _filenames = filenames.replace('*', '').lower()
                    # if filenamewithext.find(_filenames) > -1:
                    #     okay = True
                    # else:
                    #     break

                # @TODO actually allow select the file via interface
                selected_path = _item.relative_to(VALT_BASE)
                _file_raw = FileRAW()
                _file_raw.res_hash = self.res_hash
                _file_raw.set_direct(selected_path)
                return _file_raw
                # break
        return None


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
