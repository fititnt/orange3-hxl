
from abc import ABC, abstractmethod
from orangewidget.utils.signals import summarize, PartialSummary
from Orange.widgets.utils.state_summary import format_summary_details, \
    format_multiple_summaries
from AnyQt.QtCore import Qt


import os
from pathlib import Path
from genericpath import exists, isdir, isfile
import requests

from orangecontrib.hxl.widgets.utils import bytes_to_human_readable


class DataVault:

    default_data_vault: str = None
    entrypoint: str = 'rawinput'
    unzipedinput: str = 'unzipedinput'
    transformedinput: str = 'transformedinput'

    def __init__(self):
        self.default_data_vault = f'{Path.home()}/.orange3data'

    def initialize(self):
        if not exists(self.default_data_vault):
            os.makedirs(self.default_data_vault)
            os.makedirs(self.default_data_vault + '/' + self.entrypoint)
            os.makedirs(self.default_data_vault + '/' + self.unzipedinput)
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
    def resource_summary(res_group: str, res_hash: str) -> str:
        _fullpath = DataVault.resource_path(res_group, res_hash)
        if os.path.isfile(_fullpath):
            _stat = Path(_fullpath).stat()
            return {
                'files': 1,
                'size': bytes_to_human_readable(_stat.st_size),
                'path': _fullpath
            }
        elif os.path.isdir(_fullpath):
            # @TODO
            return {
                'files': -1,
                'size': -1,
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
    # Not implemented
    disk_encrypted: bool = False

    # @abstractmethod
    # def move(self):
    #     pass

    def __str__(self):
        return f'<{self.__class__.__name__}(res_hash={str(self.res_hash)})>'

    def set_resource(self, res_hash: str, res_group: str, res_alias: str = None):
        self.res_hash = res_hash
        self.res_group = res_group
        if res_alias and len(res_alias) > 0:
            self.res_alias = res_alias


class FileRAW(ResourceRAW):
    pass
    # auto_summary = False
    # res_hash: str = None
    # res_group: str = None
    # res_alias: str = 'unnamed'

    # # Not implemented
    # disk_encrypted: bool = False

    # def set_resource(self, res_hash: str, res_group: str, res_alias: str = None):
    #     self.res_hash = res_hash
    #     self.res_group = res_group
    #     if res_alias and len(res_alias) > 0:
    #         self.res_alias = res_alias

    # def summarize(self):
    #     pass


class FileRAWCollection(ResourceRAW):
    pass
    # auto_summary = False
    # res_hash: str = None
    # res_group: str = None
    # res_alias: str = 'unnamed'
    # # pass

    # def summarize(self):
    #     pass


def format_summary_details_hxl(data):
    _fullpath = DataVault.resource_path(data.res_group, data.res_hash)
    _res_summary = DataVault.resource_summary(data.res_group, data.res_hash)
    info = [
        f'Alias: <b>{data.res_alias}</b>'
        # f'Path: <b>{_fullpath}</b><br/>'
    ]
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
        'urn:data:' + data.res_group + ':' + data.res_hash + '#' + data.res_alias,
        format_summary_details_hxl(data))


@summarize.register
def summarize_(data: FileRAWCollection):
    return PartialSummary(
        'urn:data:' + data.res_group + ':' + data.res_hash + '#' + data.res_alias,
        format_summary_details_hxl(data))

# @summarize.register
# def summarize_(data: FileRAW):
#     return PartialSummary(
#         data.approx_len(),
#         format_summary_details(data, format=Qt.RichText))


# @summarize.register
# def summarize_(data: FileRAWCollection):
#     return PartialSummary(
#         data.approx_len(),
#         format_summary_details(data, format=Qt.RichText))
