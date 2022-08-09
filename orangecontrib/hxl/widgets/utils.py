from collections import namedtuple


def wkt_point_split(text: str) -> tuple:
    if not text:
        return ['', '']
    if not text.startswith('Point('):
        return ['', '']
    text_core = text.replace('Point(', '').replace(')')
    # @TODO what if have z component? Not implemented
    return text_core.split(' ')


class WKTPointSplit:
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
        # turn discrete to string variable
        column = data.get_column_view(var)[0]
        # if var.is_discrete:
        #     return [var.str_val(x) for x in column]
        return column

# class _DataType:
#     def __eq__(self, other):
#         """Equal if `other` has the same type and all elements compare equal."""
#         if type(self) is not type(other):
#             return False
#         return super().__eq__(other)

#     def __ne__(self, other):
#         return not self == other

#     def __hash__(self):
#         return hash((type(self), super().__hash__()))

#     def name_type(self):
#         """
#         Returns a tuple with name and type of the variable.
#         It is used since it is forbidden to use names of variables in settings.
#         """
#         type_number = {
#             "Categorical": 0,
#             "Real": 2,
#             "Time": 3,
#             "String": 4
#         }
#         return self.name, type_number[type(self).__name__]

# # From Orange/widgets/data/oweditdomain.py
# class Rename(_DataType, namedtuple("Rename", ["name"])):
#     """
#     Rename a variable.

#     Parameters
#     ----------
#     name : str
#         The new name
#     """
#     def __call__(self, var):
#         # type: (Variable) -> Variable
#         return var._replace(name=self.name)