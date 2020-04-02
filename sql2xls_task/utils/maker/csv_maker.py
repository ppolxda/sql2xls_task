# -*- coding: utf-8 -*-
"""
@create: 2017-10-20 16:11:32.

@author: ppolxda

@desc: CsvMaker
"""
import csv
from io import StringIO
from .maker import Maker


class CsvMaker(Maker):

    def to_csv_buffer(self):
        fs_io = StringIO()
        writer = csv.writer(fs_io, quoting=csv.QUOTE_NONNUMERIC)
        writer.writerow(self.show_cnname.values())

        for line in iter(self.sql_result.fetchall()):
            line = self._csv_rows(line)
            writer.writerow(line)
        return fs_io.getvalue().encode('gbk')
