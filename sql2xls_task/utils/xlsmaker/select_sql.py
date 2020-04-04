# -*- coding: utf-8 -*-
"""
@create: 2020-04-02 10:18:42.

@author: ppolxda

@desc: select_sql
"""
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import create_engine
# from sqlalchemy import update
# from sqlalchemy.dialects import mysql
# from .mongo_task import mongoObject


class SelectSqlResult(object):

    def __init__(self, cursor):
        self.cursor = cursor
        # TODO - must fix fetchall memery
        self._fetchall_data = self.cursor.fetchall()

    def keys(self):
        return self.cursor.keys()

    def count(self):
        datas = self.fetchall()
        return len(datas)

    def fetchall(self):
        if self._fetchall_data is None:
            self._fetchall_data = self.cursor.fetchall()
        return self._fetchall_data

    def iter_fetchall(self):
        keys = self.keys()
        for r in iter(self.fetchall()):
            yield keys, dict(zip(keys, r))


class SelectSql(object):

    def __init__(self, sql_url, sql_str, sql_parames):
        # assert isinstance(cnname, dict)
        # assert isinstance(options, dict)
        assert isinstance(sql_parames, list)

        self.sql_str = sql_str.strip()
        self.sql_url = sql_url.strip()
        self.sql_parames = sql_parames
        # self.cnname = cnname
        # self.options = options
        self.result_cursor = None

    def select(self):
        if self.result_cursor is not None:
            return self.result_cursor

        sql_str = self.sql_str.lower()
        if not sql_str.startswith('select'):
            raise TypeError('sql not select')

        # self.sql_str = self.sql_str.replace(, '?')

        if self.sql_parames:
            sql_parames = {'keys' + str(i): val
                           for i, val in enumerate(self.sql_parames)}
            sql_str = self.sql_str.split('%s')
            sql_str = [str(i - 1) + val if i != 0 else val
                       for i, val in enumerate(sql_str)]
            sql_str = ':keys'.join(sql_str)
        else:
            sql_str = self.sql_str
            sql_parames = []

        session = None
        try:
            engine = create_engine(self.sql_url, convert_unicode=True)
            sessions = sessionmaker(
                bind=engine, autocommit=False, autoflush=True
            )
            session = sessions()

            result = session.execute(sql_str, sql_parames)
            self.result_cursor = SelectSqlResult(result)
        finally:
            if session:
                session.rollback()
                session.close()

        return self.result_cursor
