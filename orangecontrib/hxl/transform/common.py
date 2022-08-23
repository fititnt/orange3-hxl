# @TODO


from abc import ABC
import inspect
import time


try:
    import pandas as pandas
except Exception:
    pass


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
