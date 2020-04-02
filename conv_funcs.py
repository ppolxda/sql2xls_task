import re
import math
import decimal

FUNC_RE = re.compile(r'^(?P<func>[a-z_]+)\((?P<opts>.+)\)$')
PARAME_RE = re.compile(r'^(?P<val>.+)::(?P<type>any|int|string|float|bool)$')


def call_func(func_name, value, fields):
    match = FUNC_RE.match(func_name)
    if not match:
        return value

    _func_name = match.group('func')
    _opts = match.group('opts').split(',')
    _opts_fmt = []

    for i in _opts:
        match = PARAME_RE.match(i.strip())
        if not match:
            return value

        _val = match.group('val')
        _type = match.group('type')

        if _val[0] == '{' and _val[-1] == '}':
            _val = fields[_val[1:-1]]

        _opts_fmt.append(conv_val(_val, _type))

    _func = FUNCS.get(_func_name, None)
    if _func:
        return _func(*_opts_fmt)

    _func = getattr(math, _func_name)
    if _func:
        return _func(*_opts_fmt)

    return value


def conv_val(_val, _type):
    if _type == 'int':
        return int(_val)
    elif _type == 'string':
        return str(_val)
    elif _type == 'float':
        return decimal.Decimal(_val)
    elif _type == 'bool':
        return bool(_val)
    elif _type == 'any':
        return _val
    else:
        raise TypeError('conv_val type invaild')


def encode_string(string):
    if len(string) > 0:
        size = len(string)
        if size <= 2:
            return string
        elif size == 3:
            return string[0] + '***' + string[2]
        elif size == 4:
            return string[0:1] + '***' + string[2:4]
        elif size == 5:
            return string[0:2] + '***' + string[3:6]
        elif size == 6:
            return string[0:2] + '***' + string[4:7]
        elif size == 7:
            return string[0:2] + '***' + string[4:8]
        elif size == 8:
            return string[0:2] + '***' + string[5:10]
        elif size == 9:
            return string[0:3] + '***' + string[6:9]
        elif size == 10:
            return string[0:3] + '***' + string[7:10]
        elif size == 11:
            return string[0:3] + '***' + string[7:11]
        else:
            temp = string[0:4]
            for i in range(0, len(string) - 8):
                temp += '*'
            return temp + string[-4:]

        return string

    return None


def add(a, b):
    return a + b


def sub(a, b):
    return a - b


def mul(a, b):
    return a * b


def div(a, b):
    return a / b


def mod(a, b):
    return a % b


FUNCS = {
    'add': add, 'sub': sub,
    'mul': mul, 'div': div,
    'mod': mod, 'round': round,
    'encode_string': encode_string
}


# def main():
#     print("'add({val}::int, 2::int)' = ",
#           call_func('add({val}::int, 2::int)', 1))
#     print("'round({val}::float, 2::int)' = ",
#           call_func('round({val}::any, 2::int)', 1.888888))


# if __name__ == '__main__':
#     main()
