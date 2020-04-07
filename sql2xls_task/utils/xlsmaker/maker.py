import codecs
from . import utils
from . import fake_funcs
from .select_sql import SelectSql
from .select_sql import SelectSqlResult
try:
    import funcs
except ImportError:
    funcs = fake_funcs
    print('running fake_funcs')


class Maker(object):

    def __init__(self, sql_result, options):
        if not isinstance(sql_result, (SelectSqlResult, SelectSql)) or \
                not isinstance(options, list):
            raise TypeError()

        if isinstance(sql_result, SelectSql):
            sql_result = sql_result.select()

        assert isinstance(options, list)
        assert isinstance(sql_result, SelectSqlResult)
        self.sql_result = sql_result
        self.options = options
        self.show_cnname = {
            l['field']: l.get('cnname', l['field'])
            for l in options
        }
        self.show_keys = [l['field'] for l in options]
        self.show_dict = {
            l['field']: l for l in options
        }

    def to_csv_file(self, file_path):
        with codecs.open(file_path, 'wb') as csvfile:
            csvfile.write(self.to_csv_buffer())

    def _csv_cols(self, colkey, colval, fields):
        try:
            return self.__csv_cols(colkey, colval, fields)
        except:  # noqa
            return colval

    def __csv_cols(self, colkey, colval, fields):
        """__csv_cols.

        options = [
            {'field': 'roleid', 'cnname': 'roleid', 'options': {"dataType": "int"}},
            {'field': 'roleid2', 'cnname': 'roleid2', 'options': {
                "dataType": "int", 'func': 'mul({roleid}::int, {roleid}::int)'
            }},
            {'field': 'email', 'cnname': 'email', 'options': {"dataType": "string"}},
            {'field': 'phone', 'cnname': 'phone', 'options': {"dataType": "string"}},
            {'field': 'roletype', 'cnname': 'roletype', 'options': {
                "dataType": "enum",
                'enums': {
                    '0': 'L',
                    '1': 'A',
                    '2': 'B',
                    '3': 'C',
                    '4': 'D',
                }
            }},
            {'field': 'rolename', 'cnname': 'rolename', 'options': {"dataType": "string"}},
        ]
        self.show_dict = {
            'field': {'field': key, 'cnname': 'cnname', 'options': {}}
        }
        """  # noqa
        show_option = self.show_dict.get(colkey, None)
        if not show_option:
            return colval

        if 'options' in show_option:
            if 'enums' in show_option['options']:
                if not isinstance(show_option['options'], dict):
                    return colval

                return show_option['options']['enums'].get(str(colval), colval)

            if 'func' in show_option['options']:
                return funcs.call_func(show_option['options']['func'],
                                       colval, fields)

        option = show_option.get('options', None)
        if not option:
            return colval

        if 'dataType' not in option:
            return colval

        elif option['dataType'] == 'string':
            if colkey == 'email':
                colval = utils.encode_email(colval)
            if colkey == 'phone':
                colval = utils.encode_string(colval)
            return utils.string_line(colval)

        elif option['dataType'] == 'int':
            return colval

        elif option['dataType'] == 'float':
            return utils.string_line('{0:f}'.format(colval))

        else:
            return colval

    def _csv_rows(self, line):
        # TODO - use dictcurr
        keys_map = {
            key: line[i]
            for i, key in enumerate(self.sql_result.keys())
        }
        return map(lambda x: self._csv_cols(
            x, keys_map.get(x, '--'), keys_map),
            self.show_keys
        )