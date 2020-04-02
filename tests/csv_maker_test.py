# -*- coding: utf-8 -*-

import os
import unittest
from sqlalchemy import Column, DateTime, Integer, String, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import create_engine

try:
    from report_task.utils.maker.select_sql import SelectSql
    from report_task.utils.maker.csv_maker import CsvMaker
except ImportError:
    import sys
    sys.path.insert(0, os.getcwd())
    from report_task.utils.maker.select_sql import SelectSql
    from report_task.utils.maker.csv_maker import CsvMaker


Base = declarative_base()
metadata = Base.metadata

CODE_PATH = os.path.abspath(os.path.dirname(__file__))
SAVE_PATH = os.path.join(CODE_PATH, 'test_result')
try:
    os.makedirs(SAVE_PATH)
except FileExistsError:
    pass
FILE_PATH = os.path.join(SAVE_PATH, 'csv_maker_test.db')
CSV_PATH = os.path.join(SAVE_PATH, 'csv_maker_test.csv')
SQLLITE_URL = 'sqlite:///' + FILE_PATH


class SysRole(Base):
    __tablename__ = 'sys_role'
    # __table_args__ = {u'schema': 'administrate'}

    createtime = Column(DateTime, nullable=False,
                        server_default=text("CURRENT_TIMESTAMP"))
    updatetime = Column(DateTime, nullable=False, server_default=text(
        "CURRENT_TIMESTAMP"))
    roleid = Column(Integer, primary_key=True)
    rolename = Column(String(32), nullable=False)
    email = Column(String(32), nullable=False)
    phone = Column(String(32), nullable=False)
    roletype = Column(String(2), nullable=False)


class TestMathFunc(unittest.TestCase):
    """Test mathfuc.py"""

    insert_count = 100

    def test_a_init(self):
        global metadata
        global SQLLITE_URL
        engine = create_engine(SQLLITE_URL, convert_unicode=True)
        sessions = sessionmaker(bind=engine, autocommit=False, autoflush=True)
        session = sessions()
        if os.path.exists(FILE_PATH):
            os.remove(FILE_PATH)
        metadata.create_all(engine)

        for i in range(self.insert_count):
            data = SysRole()
            data.roleid = i
            data.rolename = 'roleid_' + str(i)
            data.roletype = str(i % 3)
            data.email = 'emasduyahsbd@sdf.com'
            data.phone = '233333333333s2323'
            session.add(data)
        session.commit()
        print('sqllite init sucess')

    def test_b_select(self):
        """Test method add(a, b)"""
        sql_url = SQLLITE_URL
        sql = 'SELECT email, phone, roleid, rolename, roletype FROM `sys_role` LIMIT 0, 1000'.lower()  # noqa
        options = [
            {'field': 'roleid', 'cnname': 'roleid',
                'options': {"dataType": "int"}},
            {'field': 'roleid2', 'cnname': 'roleid2', 'options': {
                "dataType": "int", 'func': 'mul({roleid}::int, {roleid}::int)'
            }},
            {'field': 'email', 'cnname': 'email',
                'options': {"dataType": "string"}},
            {'field': 'phone', 'cnname': 'phone',
                'options': {"dataType": "string"}},
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
            {'field': 'rolename', 'cnname': 'rolename',
                'options': {"dataType": "string"}},
        ]
        sql_parames = []
        task = SelectSql(sql_url, sql, sql_parames)

        result = task.select()
        self.assertEqual(self.insert_count, result.count())
        # self.assertEqual(list(cnname.keys()).sort(), result.keys().sort())
        # self.assertEqual(list(options.keys()).sort(), result.keys().sort())
        self.assertIsNotNone(result.fetchall())

        maker = CsvMaker(result, options)
        self.assertIsNotNone(maker.to_csv_buffer())
        self.assertNotEqual(maker.to_csv_buffer(), '')
        maker.to_csv_file(CSV_PATH)


if __name__ == '__main__':
    unittest.main()
