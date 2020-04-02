# -*- coding: utf-8 -*-

import os
import unittest
from sqlalchemy import Column, DateTime, Integer, String, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import create_engine

try:
    from report_task.select_sql import SelectSql
except ImportError:
    import sys
    sys.path.insert(0, os.getcwd())
    from report_task.select_sql import SelectSql


Base = declarative_base()
metadata = Base.metadata

CODE_PATH = os.path.abspath(os.path.dirname(__file__))
FILE_PATH = CODE_PATH + '/test_result/tasks_sql_test.db'
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
    roletype = Column(String(2), nullable=False)


class TestMathFunc(unittest.TestCase):
    """Test mathfuc.py"""

    insert_count = 100

    def test_a_init(self):
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
            session.add(data)
        session.commit()
        # print('sqllite init sucess')

    def test_b_select(self):
        """Test method add(a, b)"""
        sql_url = SQLLITE_URL
        sql = 'SELECT roleid, rolename, roletype FROM `sys_role` LIMIT 0, 1000'.lower()  # noqa
        cnname = {
            'roleid': u'roleid',
            'rolename': u'rolename',
            'roletype': u'roletype',
        }
        options = {
            'roleid': {"dataType": "int"},
            'rolename': {"dataType": "string"},
            'roletype': {"dataType": "enum", "enum": "EnumUserTypeTranslate"},
        }
        sql_parames = []
        task = SelectSql(sql_url, sql, sql_parames)

        result = task.select()
        self.assertEqual(self.insert_count, result.count())
        self.assertEqual(list(cnname.keys()), result.keys())
        self.assertEqual(list(options.keys()), result.keys())
        self.assertIsNotNone(result.fetchall())

    # def test_minus(self):
    #     """Test method minus(a, b)"""
    #     self.assertEqual(1, minus(3, 2))

    # def test_multi(self):
    #     """Test method multi(a, b)"""
    #     self.assertEqual(6, multi(2, 3))

    # def test_divide(self):
    #     """Test method divide(a, b)"""
    #     self.assertEqual(2, divide(6, 3))
    #     self.assertEqual(2.5, divide(5, 2))


if __name__ == '__main__':
    unittest.main()
