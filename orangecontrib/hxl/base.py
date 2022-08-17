
# from orangewidget.utils.signals import summarize, PartialSummary
# from orangewidget.utils.signals import format_summary_details
# from AnyQt.QtCore import Qt


import os
from pathlib import Path
from genericpath import exists
import requests


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
            self, res_hash: str, source_uri: str, force: bool = False):
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


class FileRAW:
    # auto_summary = False
    res_hash: str = None
    res_group: str = None

    # Not implemented
    disk_encrypted: bool = False

    def set_resource(self, res_hash: str, res_group: str):
        self.res_hash = res_hash
        self.res_group = res_group

    # def summarize(self):
    #     pass


class FileRAWCollection:
    auto_summary = False
    # # pass

    # def summarize(self):
    #     pass


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
