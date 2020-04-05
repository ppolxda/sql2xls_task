# -*- coding: utf-8 -*-
"""
@create: 2017-10-20 16:11:32.

@author: ppolxda

@desc: XlsMaker
"""
import io
import xlwt
from .maker import Maker


class XlsMaker(Maker):

    def to_csv_buffer(self):
        f = io.BytesIO()
        writer = xlwt.Workbook()
        sheet = writer.add_sheet('datas')

        for i, field in enumerate(self.show_cnname.values()):
            sheet.write(0, i, field)

        r = 1
        for line in iter(self.sql_result.fetchall()):
            line = self._csv_rows(line)
            for i, field in enumerate(line):
                sheet.write(r, i, field)
            r += 1

        writer.save(f)
        f.seek(0)
        return f.read()

    # def to_csv_file(self, file_path, encoding=None):
    #     writer = self.to_csv_buffer()
    #     writer.save(file_path)
