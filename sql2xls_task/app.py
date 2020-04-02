# -*- coding: utf-8 -*-
import asyncio
import logging
from sanic import Sanic
from sanic.response import json
# from sanic.log import logger
from .utils.task import Task
from .utils.task import EnumStatus
from .utils.config_app import Settings
# import traceback
# from tenacity import retry
# from tenacity import retry_unless_exception_type


settings = Settings('report_app')
app = Sanic('report_app')
LOGGER = logging.getLogger('report_app')
task_maker = settings.task_maker


async def is_file_exist(task: Task, timeout, trycount=0):
    if timeout <= 0:
        return None

    result = task_maker.is_file_exist(task)
    if result:
        _task = task_maker.get_task_by_id(
            task.project, task.userid, task.taskid
        )

        if _task.status in [EnumStatus.FINISH, EnumStatus.CANCEL]:
            return _task

    await asyncio.sleep(1)
    return await is_file_exist(task, timeout - 1, trycount + 1)


@app.route(
    "/export/task/<project>/<userid>/add/sync",
    methods=frozenset({"POST"})
)
async def export_task(request, project, userid):
    try:
        jsondata = request.json
        if not isinstance(jsondata, dict):
            raise TypeError('json invaild')
    except Exception:
        return json({
            'error': 1,
            'message': 'request invail'
        })

    jsondata['project'] = project
    jsondata['userid'] = userid

    try:
        timeout = int(jsondata.pop('timeout'))
    except KeyError:
        timeout = settings.sync_timeout

    try:
        jsondata['mode'] = 'sync'
        task = task_maker.create_task(**jsondata)
    except Exception as ex:
        return json({
            'error': 1,
            'message': str(ex)
        })

    _task = await is_file_exist(task, timeout)
    if not _task:
        return json({
            'error': 1,
            'message': 'task wait timeout'
        })

    if _task.status != EnumStatus.FINISH:
        return json({
            'error': 2,
            'message': _task.text,
        })

    download_url = task_maker.create_download_url(task)

    return json({
        'error': 0,
        'message': 'sucess',
        'url': download_url
    })


@app.route(
    "/export/task/<project>/<userid>/add/async",
    methods=frozenset({"POST"})
)
async def export_task_async(request, project, userid):
    try:
        jsondata = request.json
        if not isinstance(jsondata, dict):
            raise TypeError('json invaild')
    except Exception:
        return json({
            'error': 1,
            'message': 'request invail'
        })

    jsondata['project'] = project
    jsondata['userid'] = userid

    try:
        jsondata['mode'] = 'async'
        task_maker.create_task(**jsondata)
    except Exception as ex:
        return json({
            'error': 1,
            'message': str(ex)
        })

    return json({
        'error': 0,
        'message': 'sucess',
    })


@app.route(
    "/export/task/<project>/<userid>/all",
    methods=frozenset({"DELETE"})
)
def export_task_delete_all(request, project, userid):
    task_maker.delete_task_all(
        project, userid
    )

    return json({
        'error': 0,
        'message': 'sucess',
    })


@app.route(
    "/export/task/<project>/<userid>/<taskid>",
    methods=frozenset({"DELETE"})
)
def export_task_delete(request, project, userid, taskid):
    task_maker.delete_task_by_id(
        project, userid, taskid
    )

    return json({
        'error': 0,
        'message': 'sucess',
    })


@app.route(
    "/export/task/<project>/<userid>/list",
    methods=frozenset({"GET"})
)
def export_task_list(request, project, userid):
    datas = task_maker.get_task_list(
        project, userid
    )

    return json({
        'error': 0,
        'message': 'sucess',
        "datas": datas
    })

# @app.route("/export/download")
# def export_download():
#     return "Hello, World!"


def main():
    LOGGER.info('webapp start')
    app.run()


if __name__ == '__main__':
    main()
