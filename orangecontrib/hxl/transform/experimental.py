

def head(file: str, lines: int = 10) -> str:
    result = ''
    # with open(file) as _file:
    #     first_line = _file.readline()
    result = ''
    with open(file) as _file:
        for x in range(lines):
            try:
                result += next(_file)
            except StopIteration:
                pass

    return result


def tail(file: str, lines: int = 10) -> str:
    # @TODO https://stackoverflow.com/questions/7167008
    #       /efficiently-finding-the-last-line-in-a-text-file
    raise NotImplementedError
    return result
