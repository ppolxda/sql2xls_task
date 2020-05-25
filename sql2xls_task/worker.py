# -*- coding: utf-8 -*-
import time
import asyncio
import logging
import traceback
from minio.error import NoSuchKey
from minio.error import ResponseError
from .utils.config import Settings
from .utils.xlsmaker.select_sql import SelectSql
from .utils.xlsmaker.xls_maker import XlsMaker
from .utils.task import Task
from .utils.task import EnumStatus

settings = Settings('sql2xls_task')
LOGGER = logging.getLogger('sql2xls_task')
ALOOP = asyncio.get_event_loop()
task_maker = settings.task_maker


async def __run_task(task: Task):
    task.status = EnumStatus.DOING
    task.error = 'doing'
    task_maker.upload_status(task)

    sql = SelectSql(task.sql_url, task.sql, task.sql_parames)
    cursor = sql.select()
    maker = XlsMaker(cursor, task.options)
    buffer = maker.to_csv_buffer()
    task_maker.upload_file(task, buffer, '.xls')

    # if result:
    #     task.status = EnumStatus.CANCEL
    #     task.error = result
    #     task.text = 'upload error'
    #     task_maker.upload_status(task)
    #     return


async def run_task():
    try:
        task = None
        task = settings.borker.pop_task()
    except Exception as ex:
        LOGGER.warning(
            'error: %s', ex
        )

    if not task:
        ALOOP.call_later(1, lambda: asyncio.ensure_future(run_task()))
        return

    try:
        s = time.time()
        LOGGER.info('[%s]start task', task.status_object)
        await __run_task(task)
    except NoSuchKey as ex:
        LOGGER.warning(
            '[%s][%.4fs]object NoSuchKey: %s',
            task.status_object,
            time.time() - s, ex
        )

        task.status = EnumStatus.CANCEL
        task.error = str(ex)
        task.text = 'object error cancel'
        settings.task_maker.upload_status(task)
    except ResponseError as ex:
        LOGGER.warning(
            '[%s][%.4fs]object ResponseError: %s',
            task.status_object,
            time.time() - s, ex
        )

        task.status = EnumStatus.CANCEL
        task.error = str(ex)
        task.text = 'object error cancel'
        settings.task_maker.upload_status(task)
    except Exception as ex:
        LOGGER.warning(
            '[%s][%.4fs]object error: %s %s',
            task.status_object,
            time.time() - s, ex,
            traceback.format_exc()
        )

        task.status = EnumStatus.CANCEL
        task.error = str(ex)
        task.text = 'error cancel'
        settings.task_maker.upload_status(task)
    else:
        LOGGER.info(
            '[%s]object finish',
            task.status_object,
            time.time() - s,
        )
        task.status = EnumStatus.FINISH
        task.error = 'finish'
        task.text = 'finish'
        task_maker.upload_status(task)
    finally:
        ALOOP.call_soon(lambda: asyncio.ensure_future(run_task()))


def main():
    try:
        LOGGER.info('sql2xls_task start')
        ALOOP.call_soon(lambda: asyncio.ensure_future(run_task()))
        ALOOP.run_forever()
    finally:
        ALOOP.run_until_complete(ALOOP.shutdown_asyncgens())
        ALOOP.close()


if __name__ == '__main__':
    main()
