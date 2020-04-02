# -*- coding: utf-8 -*-
"""
@create: 2020-04-01 06:07:29.

@author: ppolxda

@desc: task
"""
# import uuid
import io
import json
import datetime
import logging
import mimetypes
from minio import Minio
from minio.error import NoSuchKey
from minio.error import ResponseError
from .task import Task
from .task import TaskStatus
from .broker import Broker


class TaskMaker(object):

    def __init__(self, broker: Broker,
                 minio_cli: Minio, bucket_name: str,
                 logger: logging.Logger):
        self.logger = logger
        self.broker = broker
        self.minio_cli = minio_cli
        self.bucket_name = bucket_name

        # TODO - if error run not exist
        result = self.minio_cli.bucket_exists(self.bucket_name)
        if not result:
            self.minio_cli.make_bucket(self.bucket_name)

    def create_task(self, **kwargs):
        task = Task(**kwargs)
        task.check()

        # task.status_url = self.minio_cli.presigned_put_object(
        #     self.bucket_name,
        #     task.status_object,
        #     expires=datetime.timedelta(days=1)
        # )

        # task.upload_url = self.minio_cli.presigned_put_object(
        #     self.bucket_name,
        #     task.download_object,
        #     expires=datetime.timedelta(days=1)
        # )

        self.broker.push_task(task)
        return task

    def pop_task(self):
        return self.broker.pop_task()

    def delete_task_all(self, project, userid):
        for data in self.iter_task_list(project, userid):
            self.delete_task_by_id(project, userid, data['taskid'])

    def delete_task_by_id(self, project, userid, taskid):
        task = Task(project=project, userid=userid, taskid=taskid)
        self.minio_cli.remove_object(
            self.bucket_name,
            task.status_object
        )

        self.minio_cli.remove_object(
            self.bucket_name,
            task.upload_object
        )

    def iter_task_list(self, project, userid):
        objects = self.minio_cli.list_objects_v2(
            self.bucket_name, prefix='status/{}/{}/'.format(
                project, userid
            )
        )

        for obj in objects:
            # print(
            #     obj.bucket_name,
            #     obj.object_name.encode('utf-8'),
            #     obj.last_modified,
            #     obj.etag,
            #     obj.size,
            #     obj.content_type
            # )

            rsp = self.minio_cli.get_object(
                obj.bucket_name,
                obj.object_name
            )
            if rsp.status != 200:
                raise ResponseError(
                    'get_object error {}'.format(rsp.reason)
                )

            data = json.loads(rsp.data)
            yield data

    def get_task_list(self, project, userid):
        result = []
        for data in self.iter_task_list(project, userid):
            task = TaskStatus(**data)
            download = self.minio_cli.presigned_get_object(
                self.bucket_name,
                task.download_object,
                expires=datetime.timedelta(days=1)
            )
            task = task.to_task_list()
            task['url'] = download
            result.append(task)
        return result

    def is_file_exist(self, task: Task):
        try:
            return self.minio_cli.stat_object(
                self.bucket_name,
                task.download_object,
            )
        except NoSuchKey:
            return None
        except ResponseError:
            return None

    def create_download_url(self, task: Task):
        return self.minio_cli.presigned_get_object(
            self.bucket_name,
            task.download_object,
            expires=datetime.timedelta(days=1)
        )

    def get_task_by_id(self, project, userid, taskid):
        task = Task(taskid=taskid, project=project, userid=userid)

        _object = self.minio_cli.get_object(
            self.bucket_name, task.status_object
        )
        if not _object:
            return None

        if _object.status != 200:
            self.logger.warning(
                'get_task_by_id error %s', _object.reason
            )
            return None

        data = json.loads(_object.data)
        return TaskStatus(**data)

    def upload_status(self, task: TaskStatus):
        task.update = str(datetime.datetime.now())
        data = task.to_json().encode('utf8')
        buf = io.BytesIO(data)

        return self.minio_cli.put_object(
            self.bucket_name, task.status_object,
            buf, len(data),
            content_type='application/json'
        )

    def upload_file(self, task: TaskStatus, buffer, filetype):
        task.update = str(datetime.datetime.now())
        data = task.to_json().encode('utf8')
        buf = io.BytesIO(data)

        return self.minio_cli.put_object(
            self.bucket_name, task.upload_object,
            buf, len(data),
            content_type=mimetypes.types_map[filetype]
        )
