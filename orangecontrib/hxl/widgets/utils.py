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

# pytest
#    python3 -m doctest orangecontrib/hxl/widgets/utils.py

from abc import ABC
from genericpath import exists
import inspect
import json
import logging
import sys
import time

from typing import Any, Callable, Tuple, Union

import zlib
from zipfile import ZipFile
# import pandas as pd
import pandas as pandas

from orangecontrib.hxl.L999999999_0 import (
    hxl_hashtag_normalizatio,
    hxl_hashtag_to_bcp47,
    # hxltm_carricato,
    # qhxl_hxlhashtag_2_bcp47,
    # # (...)
)
from Orange.data import Domain, Table

from Orange.widgets.data.owcsvimport import (
    pandas_to_table as _orange_pandas_to_table
)

log = logging.getLogger(__name__)


HXL_BASE_ASSUME_IMPLICIT_HASHTAG = {
    'item+conceptum': '#item+conceptum',
    'item+rem': '#item+rem',
    'meta+rem': '#meta+rem',
    'status+rem': '#status+rem',
    'date+rem': '#date+rem',
}


def hash_intentionaly_weak(text) -> str:
    return zlib.crc32(bytes(text, "utf8"))


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


def memory_usage_of(reference: Any) -> str:
    # Imperfect, but better than nothing
    # @see https://stackoverflow.com/questions/449560/how-do-i-determine-the-size-of-an-object-in-python
    # @see https://stackoverflow.com/questions/46542283/python-how-to-get-size-of-all-objects-in-current-namespace
    size_in_bytes = sys.getsizeof(reference)
    size = bytes_to_human_readable(size_in_bytes)

    # @see https://stackoverflow.com/questions/39100971/how-do-i-release-memory-used-by-a-pandas-dataframe
    #      Humm... maybe call a different thread could allow OS claimn memory back
    return size


def bytes_to_human_readable(size, precision=2):
    """bytes_to_human_readable

    Author: https://stackoverflow.com/a/32009595/894546

    Args:
        size (_type_): size in bytes
        precision (int, optional): the precision. Defaults to 2.

    Returns:
        str: the result
    """
    suffixes = ['B', 'KB', 'MB', 'GB', 'TB']
    suffixIndex = 0
    while size > 1024 and suffixIndex < 4:
        suffixIndex += 1  # increment the index of the suffix
        size = size/1024.0  # apply the division
    return "%.*f%s" % (precision, size, suffixes[suffixIndex])


def file_raw_info(source: str):

    if not exists(source):
        return f'File not exists [{source}]'

    information = "====================RAW DATA====================\n"
    # with open(source, 'rb') as f:
    #     information = f.read()[:-4]

    maxloop = 1024 * 2

    # with open(source, "rb") as f:
    # @TODO do differnty if is binary
    with open(source, "r") as f:
        byte = f.read(1)
        information += byte
        while byte and maxloop > 0:
            # Do stuff with byte.
            # byte = f.read(1)
            information += f.read(1)
            maxloop -= 1

    information += "\n====================RAW DATA===================="

    return information


def file_unzip(source: str, target: str):

    # Create a ZipFile Object and load sample.zip in it
    with ZipFile(source, 'r') as zipObj:
        # Extract all the contents of zip file in current directory
        zipObj.extractall(target)

    log.exception(f'file_unzip [{str(source)}] [{str(target)}]')


def function_ast(func: Callable, parsed: bool = False):
    """function_ast _summary_

    _extended_summary_

    Args:
        func (Callable): _description_

    Returns:
        _type_: _description_
    """
    sig = inspect.signature(func)
    if not parsed:
        return sig

    def _get_types_or_default(
            param: str, name: str, get_default=False) -> list:
        # colspecs: 'list[tuple[int, int]] | str | None' = 'infer'
        res = str(param).replace(name + ': ', '')
        # 'list[tuple[int, int]] | str | None' = 'infer'
        if res.find(' = ') > -1:
            if get_default:
                return res.split(' = ')[1]
            res = res.split(' = ')[0]
            # 'list[tuple[int, int]] | str | None'
        elif get_default:
            return '__NO_DEFAULT'
        res = res.strip('\'')
        # list[tuple[int, int]] | str | None
        if res.find(' | ') > -1:
            res = res.split(' | ')
        else:
            res = [res]
        # ['list[tuple[int, int]]', 'str', 'None']
        return res

    fun_sig_ast = {}
    index = 1
    for key, value in sig.parameters.items():
        fun_sig_ast[key] = {
            'index': index,
            'types': _get_types_or_default(value, key)
        }
        index += 1
        _def = _get_types_or_default(value, key, True)
        if _def and _def != '__NO_DEFAULT':
            fun_sig_ast[key]['default'] = _def

    return fun_sig_ast


def function_prepare_args(
    func: Callable, named_arguments: dict
) -> Tuple[dict, dict]:
    """function_prepare_args _summary_

    _extended_summary_

    Args:
        func (Callable): Function which will apply the command
        named_arguments (dict): arguments to prepare

    Returns:
        Tuple(dict, dict): Okay arguments, Failed arguments

    >>> function_prepare_args(
    ...     pandas.read_fwf, {'colspecs': 'None', 'err': 'or'})
    ({'colspecs': None}, {'err': 'or'})

    >>> function_prepare_args(
    ...     sum, {'colspecs': 'None', 'err': 'or'})
    (None, {'colspecs': 'None', 'err': 'or'})

    """
    okay = {}
    invalid = {}
    # sig = function_ast(func)
    fun_sig_ast = function_ast(func, True)
    # print(sig)

    def _try_cast_type(types: list, value: str) -> Any:
        value = value.strip('"').strip('\'')
        if value == 'None':
            return None
        if 'bool' in types:
            if value == 'False':
                return False
            if value == 'True':
                return True
        if value.isnumeric():
            if 'int' in types and 'float' not in types:
                return int(value)
            if 'int' in types and 'float' in types:
                if value.find('.') > -1:
                    return float(value)
                else:
                    return int(value)
            if value.find('.') > -1 or \
                    ('int' not in types and 'float' in types):
                return float(value)
            else:
                return int(value)
        # @TODO implement some typehint for lists, typed lists, etc
        return value

    # print(fun_sig_ast)
    # return fun_sig_ast
    for key, value in named_arguments.items():
        if key in fun_sig_ast:
            # print(sig.parameters[key])
            # print(_get_types(sig.parameters[key], key))
            value_cast = _try_cast_type(fun_sig_ast[key]['types'], value)
            okay[key] = value_cast
        else:
            invalid[key] = value
    if len(okay.keys()) == 0:
        okay = None
    if len(invalid.keys()) == 0:
        invalid = None

    return okay, invalid


def function_and_args_textarea(
        func: Callable,
        text_arguments: str,
        block_repeated: bool = True,
        *args_ordered) -> Tuple[dict, dict]:

    lines_with_comments = text_arguments.splitlines()
    named_arguments = {}
    for _line in lines_with_comments:
        if len(_line.strip()) > 0 and not _line.strip().startswith('#') and \
                _line.find('=') > -1:
            parts = _line.strip().split('=')
            key = parts.pop(0)
            # Maybe theres = in the values
            value = '='.join(parts)
            named_arguments[key] = value
            # named_arguments

    okay, invalid = function_prepare_args(func, named_arguments)
    return okay, invalid


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
        # 'total': -1,
        'prefix_hash': 0
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


def orange_data_roles_ex_hxl(
    orange_table: Table,
    hxl_h_meta: list = None,
    hxl_a_meta: list = None,
    hxl_h_ignore: list = None,
    hxl_a_ignore: list = None,
) -> Table:

    _is_debug = True
    changes = {
        'from': {
            'attribute': 0,
            'class': 0,
            'ignore': 0,
            'meta': 0,
        },
        'to': {
            'attribute': 0,
            'class': 0,
            'ignore': 0,
            'meta': 0,
        },
        'total': 0,
    }
    if _is_debug:
        changes['_debug'] = []

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

    def _needs_change(hashtag: str, status_quo: str) -> bool:
        """_needs_change

        Return string with target group if necessary. It will always try
        stay with current Orange3 Roles before trying change to new ones
        """
        # return 'meta'
        if not hashtag or not hashtag.startswith('#'):
            return False

        log.exception(
            f'>>> _needs_change test [{hashtag}] [{hxl_h_meta} {hxl_a_meta}]')
        log.exception(qhxl_match(hashtag, hxl_h_meta,
                      hxl_a_meta, op_and=False))

        if status_quo == 'meta' and \
                qhxl_match(hashtag, hxl_h_meta, hxl_a_meta, op_and=False):
            return False
        if status_quo == 'ignore' and \
                qhxl_match(hashtag, hxl_h_ignore, hxl_a_ignore, op_and=False):
            return False

        # Common case: status_quo=attributes
        # Common case: status_quo=class
        if status_quo != 'meta' and \
                qhxl_match(hashtag, hxl_h_meta, hxl_a_meta, op_and=False):
            return 'meta'
        if status_quo != 'ignore' and \
                qhxl_match(hashtag, hxl_h_ignore, hxl_a_ignore, op_and=False):
            return 'ignore'

        return None

    needs_update = False
    # new_attributes = []
    # history_new_names = []

    resultatum = {
        'attributes': [],
        'class': [],
        'meta': [],
        'ignore': [],
    }

    for item in orange_table.domain.attributes:
        changes['total'] += 1
        statum_novo = _needs_change(item.name, 'attributes')

        if statum_novo:
            needs_update = True
            changes['from']['attribute'] += 1
            changes['to'][statum_novo] += 1
            if _is_debug:
                changes['_debug'].append(
                    f'attribute->{statum_novo}[{item.name}]')
            resultatum[statum_novo].append(item)
        else:
            resultatum['attributes'].append(item)

    for item in orange_table.domain.metas:
        changes['total'] += 1
        statum_novo = _needs_change(item.name, 'meta')

        if statum_novo:
            needs_update = True
            changes['from']['meta'] += 1
            changes['to'][statum_novo] += 1
            if _is_debug:
                changes['_debug'].append(f'meta->{statum_novo}[{item.name}]')
            resultatum[statum_novo].append(item)
        else:
            resultatum['meta'].append(item)

    for item in orange_table.domain.class_vars:
        changes['total'] += 1
        statum_novo = _needs_change(item.name, 'class')

        if statum_novo:
            needs_update = True
            changes['from']['class'] += 1
            changes['to'][statum_novo] += 1
            if _is_debug:
                changes['_debug'].append(f'class->{statum_novo}[{item.name}]')
            resultatum[statum_novo].append(item)
        else:
            resultatum['class'].append(item)

    log.exception(
        f'>>> orange_data_roles_ex_hxl meta')
    log.exception(changes)

    if needs_update:
        log.exception(
            f'>>> orange_data_roles_ex_hxl changes necessary')
        # new_domain = Domain(
        #     new_attributes,
        #     new_class_vars, new_metas
        # )
        new_domain = Domain(
            resultatum['attributes'],
            resultatum['class'],
            resultatum['meta']
        )
        extended_data = orange_table.transform(new_domain)
        # return extended_data, None
        return extended_data, changes
    else:
        log.exception(
            f'>>> orange_data_roles_ex_hxl no changes necessary')
        return orange_table, changes


def pandas_to_table(df) -> Table:
    """pandas_to_table"""
    return _orange_pandas_to_table(df)


def string_to_list(
        text: str,
        delimiters: list = None,
        default: Any = None,
        prefix: str = None,
        strip_prefix: bool = False
) -> Union[list, Any]:
    """string_to_list Split text into a list

    Args:
        text (str): _description_
        delimiters (list, optional): _description_.
        default (Any, optional): _description_.
        prefix (str, optional): If given, require items have this.
        strip_prefix (bool, optional): Remove prefix from items.

    Returns:
        Union[list, Any]: the result

    >>> string_to_list('a, b, c')
    ['a', 'b', 'c']

    >>> string_to_list(None)

    >>> string_to_list('a, b,| c', delimiters=['|'])
    ['a, b,', 'c']

    >>> string_to_list(
    ...   '+aa+bb | +cc | dd', delimiters=['|'], prefix='+', strip_prefix=False)
    ['+aa+bb', '+cc']

    """
    result = []
    if text and isinstance(text, str):
        if delimiters is None:
            delimiters = ['|', ',', "\t"]
        for ditem in delimiters:
            # ASCII: 29 GS (Group separator)
            text = text.replace(ditem, chr(29))
        # result = filter(None, map(str.strip, text.split(',')))
        result = list(filter(None, map(str.strip, text.split(chr(29)))))
        if prefix:
            result = [x for x in result if x.startswith(prefix)]
            if strip_prefix and len(result) > 0:
                result = [x.replace(prefix, '') for x in result]

    if len(result) == 0:
        return default

    return result


def qhxl_match(
    hashtag: str,
    search_hashtags: list = None,
    search_attributes: list = None,
    op_and: bool = True,
    # base_hashtags_op_or: bool = False, # this would not make sense
) -> bool:
    """qhxl_match Check if a full HXL hashtag matches a request

    Args:
        hashtag (str): The full hashtag
        search_hashtags (list, optional): _description_. Defaults to None.
        search_attributes (list, optional): _description_. Defaults to None.
        op_and (bool, optional): _description_. Defaults to True.

    Returns:
        bool: _description_
    >>> qhxl_match('#meta+id', None, ['+id'])
    True
    >>> qhxl_match('#meta+name', None, ['+id', '+code'])
    False
    >>> qhxl_match('#meta+alt2+name', None, ['+alt+name', '+name+alt2'])
    True
    >>> qhxl_match('#meta+alt2+name', None, ['+name+alt2'])
    True
    >>> qhxl_match('#meta+alt+name', ['#country'], ['+name+alt'])
    False
    >>> qhxl_match('#meta+alt+name', ['#country'], ['+name+alt'], op_and=False)
    True
    """
    if not hashtag or not hashtag.startswith('#') or hashtag.find('+') == -1:
        return None
    _okay_h = False if search_hashtags else None
    _okay_a = False if search_attributes else None

    _parts = hashtag.split('+')
    _de_facto_basi = _parts.pop(0).strip()
    _de_facto_attrs = _parts

    if search_hashtags and f'#{_de_facto_basi}' in search_hashtags:
        _okay_h = True
    if search_attributes:
        for sitem in search_attributes:
            # sitem_attrs = sitem.strip().split('+')
            sitem_attrs = list(filter(None, map(str.strip, sitem.split('+'))))
            # print('sitem_attrs', sitem_attrs)
            if len(sitem_attrs) == 0:
                continue
            _sitems_left = len(sitem_attrs)
            for _attr_item in sitem_attrs:
                if _attr_item in _de_facto_attrs:
                    _sitems_left -= 1
            if _sitems_left == 0:
                # print('okay a')
                _okay_a = True
                break

    # print('_de_facto_attrs', _de_facto_attrs)
    # print('_okay_h', _okay_h)
    # print('_okay_a', _okay_a)
    # print('_sitems_left', _sitems_left)
    if (_okay_h is True and _okay_a is True) or \
            (op_and is False and (_okay_h is True or _okay_a is True)):
        return True
    if (_okay_h is None and _okay_a is True) or \
            (_okay_h is True and _okay_a is None):
        return True

    return False


RAW_FILE_EXPORTERS = {
    # '': None,
    'pandas.read_table': pandas.read_table,
    'pandas.read_csv': pandas.read_csv,
    'pandas.read_excel': pandas.read_excel,
    'pandas.read_feather': pandas.read_feather,
    'pandas.read_fwf': pandas.read_fwf,
    'pandas.read_html': pandas.read_html,
    'pandas.read_json': pandas.read_json,
    'pandas.json_normalize': pandas.json_normalize,
    'pandas.read_orc': pandas.read_orc,
    'pandas.read_parquet': pandas.read_parquet,
    'pandas.read_sas': pandas.read_sas,
    'pandas.read_spss': pandas.read_spss,
    'pandas.read_stata': pandas.read_stata,
    'pandas.read_xml': pandas.read_xml,
}

RAW_FILE_EXPORTERS_UI = RAW_FILE_EXPORTERS.keys()


class RawFileCommonUtils(ABC):
    signature: str = None
    _errors: list = []
    _errors_max = 5

    def __init__(self, signature: str = None) -> None:
        if signature:
            self.signature = signature

    def _set_error(self, info: str):
        timestring = time.strftime("%H:%M:%S")
        # t = strings.split(',')
        if len(self._errors) > self._errors_max:
            self._errors.pop()
        self._errors.insert(0, f'{timestring} ❌ {info}')

    def _get_func_by_alias(self, signature: str):
        if not signature or signature.count('.') != 1:
            raise NotImplementedError(signature)
        lib, fun = signature.split('.')
        if lib == 'pandas':
            the_function = getattr(pandas, fun)
            return the_function
        else:
            # return f'@TODO {signature}'
            raise NotImplementedError(signature)

    def user_help(self, signature: str = None):
        _signature = signature if signature else self.signature
        if not _signature:
            return 'Error, no help found'
        # _signature = _signature.replace('.', '__')

        lib, fun = _signature.split('.')
        if lib == 'pandas':
            the_function = getattr(pandas, fun)
            # the_signature = inspect.signature(the_function)
            _help_text = _signature
            _help_text += "\n\n" + str(inspect.signature(the_function))
            _help_text += "\n" + the_function.__doc__
            return _help_text
        else:
            return f'@TODO {signature}'


class RawFileExporter(RawFileCommonUtils):

    def get_compiled_arguments(self, exporter: str, text_arguments: str):
        func = self._get_func_by_alias(exporter)
        okay, invalid = function_and_args_textarea(func, text_arguments)
        return okay, invalid

    def get_all_available_options(self) -> list:
        """get_all_available_options Return a list with what could be used

        Returns:
            list: the result
        """
        # @TODO check before based on installed libraries
        return RAW_FILE_EXPORTERS.keys()

    def try_run(self, exporter: str, resource: str, args: dict = None):
        _method = exporter.replace('.', '__') if exporter else '_failed'

        if _method not in dir(__class__):
            ex_type, ex_value, ex_traceback = sys.exc_info()
            self._set_error(f'Unknown exporter {str(exporter)}')
            return None
        try:
            # @TODO maybe allow check if user have more options than need
            # return self[_method](resource, args)
            # log.exception(
            #     f'exporter[{exporter}] resource[{str(resource)}] args[{str(args)}]')

            if args and 'args' in args:
                args = args['args']

            # args = {}
            # args['delimiter'] = ','
            # args['sep'] = ','

            if args:
                return getattr(self, _method)(resource, **args)
            else:
                return getattr(self, _method)(resource)
        # except (ValueError, AttributeError) as ex:
        except Exception as ex:
            # https://stackoverflow.com/questions/4690600/python-exception-message-capturing
            # Get current system exception
            ex_type, ex_value, _ex_traceback = sys.exc_info()
            # self._set_error(f'[{exporter}] [{_method}] [{str(ex_type)}] {str(ex_value)}')
            self._set_error(f'[{exporter}] [{str(ex_type)}] {str(ex_value)}')
            log.exception(f'[{exporter}] [{str(ex_type)}] {str(ex_value)}')
            # self._set_error(f'self[{_method}]({resource}, {args})')
            return None

    def why_failed(self, formated: bool = True):
        if formated:
            # if len(self._errors) == 0:
            #     return 'No errors'
            result = ''
            for line in self._errors:
                result += str(line) + "\n"
                # result += str(line)

            # return "\n".join(self._errors)
            return result

            # return json.dumps(
            #     self._errors, indent=4, sort_keys=True, ensure_ascii=False)
        return self._errors

    def pandas__json_normalize(self, file, **kwargs):
        return pandas.json_normalize(file, **kwargs)

    def pandas__read_csv(self, file, **kwargs):
        return pandas.read_csv(file, **kwargs)

    def pandas__read_excel(self, file, **kwargs):
        return pandas.read_excel(file, **kwargs)

    def pandas__read_fwf(self, file, **kwargs):
        return pandas.read_fwf(file, **kwargs)

    def pandas__read_feather(self, file, **kwargs):
        return pandas.read_feather(file, **kwargs)

    def pandas__read_html(self, file, **kwargs):
        return pandas.read_html(file, **kwargs)

    def pandas__read_json(self, file, **kwargs):
        return pandas.read_json(file, **kwargs)

    def pandas__read_table(self, file, **kwargs):
        return pandas.read_table(file, **kwargs)

    def pandas__read_orc(self, file, *args):
        return pandas.read_orc(file)

    def pandas__read_parquet(self, file, **kwargs):
        return pandas.read_parquet(file, **kwargs)

    def pandas__read_sas(self, file, **kwargs):
        return pandas.read_sas(file)

    def pandas__read_spss(self, file, **kwargs):
        return pandas.read_spss(file, **kwargs)

    def pandas__read_stata(self, file, **kwargs):
        return pandas.read_stata(file)

    def pandas__read_xml(self, file, **kwargs):
        return pandas.read_xml(file, **kwargs)


# def rawfile_csv_to_pandas(file) -> pandas.DataFrame:
#     return pandas.read_csv(file)


# def rawfile_json_to_pandas(file) -> pandas.DataFrame:
#     # pandas.read_json
#     return pandas.read_json(file)


# def rawfile_json_normalize_to_pandas(file) -> pandas.DataFrame:
#     # pandas.json_normalize
#     return pd.json_normalize(file)
