# ==============================================================================
#
#          FILE:  utils.py
#                 orangecontrib.hxl.utils
#
#         USAGE:  Its a library for Orange Data Mining software.
#
#   DESCRIPTION:  ---
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
#       CREATED:  2022-08-09 15:48 UTC started
#      REVISION:  ---
# ==============================================================================
"""utils
"""

import logging
from typing import Tuple
from orangecontrib.hxl.L999999999_0 import (
    hxl_hashtag_normalizatio,
    hxl_hashtag_to_bcp47,
    # hxltm_carricato,
    # qhxl_hxlhashtag_2_bcp47,
    # # (...)
)
from Orange.data import Domain, Table

log = logging.getLogger(__name__)


HXL_BASE_ASSUME_IMPLICIT_HASHTAG = {
    'item+conceptum': '#item+conceptum',
    'item+rem': '#item+rem',
    'meta+rem': '#meta+rem',
    'status+rem': '#status+rem',
    'date+rem': '#date+rem',
}


def wkt_point_split(text: str) -> tuple:
    """wkt_point_split"""
    if not text:
        return [None, None]
        # return ['', '']
    if not text.startswith('Point('):
        return [None, None]
        # return ['', '']

    text_core = text.replace('Point(', '').replace(')', '')
    # @TODO what if have z component? Not implemented
    parts = text_core.split(' ')
    return [float(parts[0]), float(parts[1])]
    # return text_core.split(' ')


class WKTPointSplit:
    """WKTPointSplit"""

    def __init__(self, data, attr, delimiter=' '):
        self.attr = attr
        self.delimiter = delimiter

        column = self.get_string_values(data, self.attr)
        values = [s.split(self.delimiter) for s in column]
        self.new_values = tuple(sorted({val if val else "?" for vals in
                                        values for val in vals}))

    def __eq__(self, other):
        return self.attr == other.attr and self.delimiter == \
            other.delimiter and self.new_values == other.new_values

    def __hash__(self):
        return hash((self.attr, self.delimiter, self.new_values))

    def __call__(self, data):
        column = self.get_string_values(data, self.attr)
        values = [set(s.split(self.delimiter)) for s in column]
        shared_data = {v: [i for i, xs in enumerate(values) if v in xs] for v
                       in self.new_values}
        return shared_data

    @staticmethod
    def get_string_values(data, var):
        """get_string_values"""
        # turn discrete to string variable
        column = data.get_column_view(var)[0]
        # if var.is_discrete:
        #     return [var.str_val(x) for x in column]
        return column


def sortname(name: str, name_list: list = None) -> str:
    if not name.startswith('#') and \
            (name.startswith('item+') or
                name.startswith('status+') or
             name.startswith('date+')):
        name = '#' + name

    # if name.startswith('#'):
    #     maybe = hxl_hashtag_to_bcp47(name)
    #     return bcp47_shortest_name(maybe)
    if name.startswith('#'):
        maybe = hxl_hashtag_to_bcp47(name)
        if maybe and maybe['Language-Tag_normalized']:
            return bcp47_shortest_name(
                maybe['Language-Tag_normalized'], name_list)

    return bcp47_shortest_name(name, name_list)


def bcp47_shortest_name(name: str, name_list: list = None):
    """bcp47_shortest_name"""
    # @TODO finish this draft
    # @TODO consider name_list to avoid create duplicates

    if name.find('qcc-Zxxx-r-aMDCIII-alatcodicem') > -1 or \
            name.find('sU2200') > -1:
        # For now, lets avoid mess with global identifiers
        return name

    if name.find('-x-') > -1:
        parts = name.split('-x-')
        name = 'x-' + parts[1]

    if name.find('qcc-Zxxx-r') > -1:
        name = name.replace('qcc-Zxxx-r', '')

    if name.find('qcc-Zxxx') > -1:
        name = name.replace('qcc-Zxxx', '')

    name_minimal = name
    attempt = 0
    while name in name_list:
        name = f'{name_minimal}-zzi{str(attempt)}'
        # name = name_minimal + '-zzq'
        attempt += 1

    return name
# Tuple[str, List[float], int]:


def orange_data_names_normalization(
        orange_table: Table, hashtag_add: bool = True) -> Tuple[Table, dict]:
    """orange_data_names_normalization Normalize HXL hashtags from data columns

    This will apply L999999999_0.hxl_hashtag_normalizatio() to column names
    if they likely to be an HXLTM hashtag. The consequence is mostly remove
    duplicated attributes and

    Args:
        orange_table (Table): _description_
        hashtag_add (bool, optional): _description_. Defaults to True.

    Returns:
        Table: _description_
    """
    changes = {
        'total': -1,
        'prefix_hash': -1
    }
    # log.exception(' >>>> self.data.domain.attributes')
    # log.exception(type(self.data.domain.attributes))
    # log.exception(self.data.domain.attributes)
    # log.exception(' >>>> self.data.domain.class_vars')
    # log.exception(type(self.data.domain.class_vars))
    # log.exception(self.data.domain.class_vars)
    # log.exception(' >>>> self.data.domain.metas')
    # log.exception(type(self.data.domain.metas))
    # log.exception(self.data.domain.metas)

    def _normalize(textum: str) -> str:
        if not textum.startswith('#'):
            for ref, val in HXL_BASE_ASSUME_IMPLICIT_HASHTAG.items():
                if textum.startswith(ref):
                    textum = textum.replace(ref, val)
                    break
        if not textum.startswith('#'):
            # We avoid try "fix" variables user may adding to the datasets
            return textum

        return hxl_hashtag_normalizatio(textum)

    needs_update = False
    new_attributes = []
    history_new_names = []
    for item in orange_table.domain.attributes:
        new_name = _normalize(item.name)
        history_new_names.append(new_name)
        if new_name != item.name:
            needs_update = True
            item = item.renamed(new_name)
        new_attributes.append(item)

    new_metas = []
    for item in orange_table.domain.metas:
        new_name = _normalize(item.name)
        history_new_names.append(new_name)
        if new_name != item.name:
            needs_update = True
            item = item.renamed(new_name)
        new_metas.append(item)

    new_class_vars = []
    for item in orange_table.domain.class_vars:
        new_name = _normalize(item.name)
        history_new_names.append(new_name)
        if new_name != item.name:
            needs_update = True
            item = item.renamed(new_name)
        new_class_vars.append(item)

    if needs_update:
        log.exception(
            f'>>> orange_data_names_normalization changes necessary')
        new_domain = Domain(
            new_attributes,
            new_class_vars, new_metas
        )
        extended_data = orange_table.transform(new_domain)
        return extended_data, None
    else:
        log.exception(
            f'>>> orange_data_names_normalization no changes necessary')
        return orange_table, changes


def orange_data_roles_ex_hxl(orange_table: Table) -> Table:
    # (...)
    # log.exception(
    #     f'>>> orange_data_roles_ex_hxl orange_table.domain.attributes {orange_table.domain.attributes}')
    # log.exception(
    #     f'>>> orange_data_roles_ex_hxl orange_table.domain.metas {orange_table.domain.metas}')
    # log.exception(
    #     f'>>> orange_data_roles_ex_hxl orange_table.domain.class_vars {orange_table.domain.class_vars}')
    extended_data = orange_table
    return extended_data
