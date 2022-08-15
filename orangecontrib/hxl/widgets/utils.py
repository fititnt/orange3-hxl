"""utils
"""
from orangecontrib.hxl.L999999999_0 import (
    hxl_hashtag_to_bcp47,
    # hxltm_carricato,
    # qhxl_hxlhashtag_2_bcp47,
    # # (...)
)


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
