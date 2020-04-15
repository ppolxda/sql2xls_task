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

    result = task_maker.is_status_exist(task)
    if result:
        _task = task_maker.get_task_by_id(
            task.project, task.user, task.taskid
        )

        if _task and _task.status in [
            EnumStatus.FINISH, EnumStatus.CANCEL
        ]:
            return _task

    await asyncio.sleep(1)
    result = await is_file_exist(task, timeout - 1, trycount + 1)
    return result


@app.route(
    "/export/task/<project>/<user>/add/sync",
    methods=frozenset({"POST"})
)
async def export_task(request, project, user):
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
    jsondata['user'] = user

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
    "/export/task/<project>/<user>/add/async",
    methods=frozenset({"POST"})
)
async def export_task_async(request, project, user):
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
    jsondata['user'] = user

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
    "/export/task/<project>/<user>/all",
    methods=frozenset({"DELETE"})
)
def export_task_delete_all(request, project, user):
    try:
        task_maker.delete_task_all(
            project, user
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
    "/export/task/<project>/<user>/<taskid>",
    methods=frozenset({"DELETE"})
)
def export_task_delete(request, project, user, taskid):
    try:
        task_maker.delete_task_by_id(
            project, user, taskid
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
    "/export/task/<project>/<user>/list",
    methods=frozenset({"GET"})
)
def export_task_list(request, project, user):
    try:
        datas = task_maker.get_task_list(
            project, user
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
        prefix = args.get('prefix', '')
        expires = int(args.get('expires', 60))

        if prefix and prefix[0] != '/':
            prefix = ''.join(['/', prefix])

        url = res_maker.presigned_put_object(
            project, prefix, ftype, expires
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


@app.route(
    "/res/<project>/list",
    methods=frozenset({"GET"})
)
async def resources_res_list(request, project):
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
        prefix = args.get('prefix', '')
        expires = int(args.get('expires', 60))
        if prefix and prefix[0] != '/':
            prefix = ''.join(['/', prefix])

        objects = res_maker.get_objects_list(
            project, prefix
        )
    except Exception as ex:
        return json({
            'error': 1,
            'message': str(ex)
        })

    return json({
        'error': 0,
        'message': 'sucess',
        'objects': [
            res_maker.presigned_get_object(i.object_name, expires)
            for i in objects
        ]
    })


def main():
    LOGGER.info('webapp start')
    app.run(host=settings.app_host, port=settings.app_port)


if __name__ == '__main__':
    main()
