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
res_maker = settings.res_maker


# ----------------------------------------------
#        Export
# ----------------------------------------------


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
    try:
        task_maker.delete_task_all(
            project, userid
        )
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
    "/export/task/<project>/<userid>/<taskid>",
    methods=frozenset({"DELETE"})
)
def export_task_delete(request, project, userid, taskid):
    try:
        task_maker.delete_task_by_id(
            project, userid, taskid
        )
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
    "/export/task/<project>/<userid>/list",
    methods=frozenset({"GET"})
)
def export_task_list(request, project, userid):
    try:
        datas = task_maker.get_task_list(
            project, userid
        )
    except Exception as ex:
        return json({
            'error': 1,
            'message': str(ex)
        })

    return json({
        'error': 0,
        'message': 'sucess',
        "datas": datas
    })


# ----------------------------------------------
#        Resources
# ----------------------------------------------


@app.route(
    "/res/<project>",
    methods=frozenset({"GET"})
)
async def resources_presigned(request, project):
    try:
        args = request.args
        if not isinstance(args, dict) or not request.args:
            raise TypeError('query_args invaild')
    except Exception:
        return json({
            'error': 1,
            'message': 'request invail'
        })

    try:
        ftype = args.get('type', '')
        expires = int(args.get('expires', 60))
        url = res_maker.presigned_put_object(
            project, ftype, expires
        )
    except Exception as ex:
        return json({
            'error': 1,
            'message': str(ex)
        })

    return json({
        'error': 0,
        'message': 'sucess',
        'url': url
    })


def main():
    LOGGER.info('webapp start')
    app.run(host=settings.app_host, port=settings.app_port)


if __name__ == '__main__':
    main()
