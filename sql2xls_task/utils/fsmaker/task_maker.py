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
from minio.error import BucketAlreadyExists
from minio.error import BucketAlreadyOwnedByYou
from ..task import Task
from ..task import TaskStatus
from ..broker import Broker


class TaskMaker(object):

    def __init__(self, broker: Broker, minio_cli: Minio,
                 bucket_name: str, bucket_location: str,
                 logger: logging.Logger):
        self.logger = logger
        self.broker = broker
        self.minio_cli = minio_cli
        self.bucket_name = bucket_name
        self.bucket_location = bucket_location
        self.is_bucket_create = False

    def create_bucket_if_not_exists(self):
        if self.is_bucket_create:
            return

        try:
            self.minio_cli.make_bucket(self.bucket_name, self.bucket_location)
        except BucketAlreadyOwnedByYou:
            pass
        except BucketAlreadyExists:
            pass
        except ResponseError:
            raise

        self.is_bucket_create = True

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

    def delete_task_all(self, project, user):
        for data in self.iter_task_list(project, user):
            self.delete_task_by_id(project, user, data['taskid'])

    def delete_task_by_id(self, project, user, taskid):
        task = Task(project=project, user=user, taskid=taskid)

        self.create_bucket_if_not_exists()

        self.minio_cli.remove_object(
            self.bucket_name,
            task.status_object
        )

        self.minio_cli.remove_object(
            self.bucket_name,
            task.upload_object
        )

    def iter_task_list(self, project, user):
        self.create_bucket_if_not_exists()
        objects = self.minio_cli.list_objects_v2(
            self.bucket_name, prefix='status/{}/{}/'.format(
                project, user
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

    def get_task_list(self, project, user):
        self.create_bucket_if_not_exists()

        result = []
        for data in self.iter_task_list(project, user):
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

    def is_status_exist(self, task: Task):
        try:
            self.create_bucket_if_not_exists()
            return self.minio_cli.stat_object(
                self.bucket_name,
                task.status_object,
            )
        except NoSuchKey:
            return None
        except ResponseError:
            return None

    def is_file_exist(self, task: Task):
        try:
            self.create_bucket_if_not_exists()
            return self.minio_cli.stat_object(
                self.bucket_name,
                task.download_object,
            )
        except NoSuchKey:
            return None
        except ResponseError:
            return None

    def create_download_url(self, task: Task):
        self.create_bucket_if_not_exists()
        return self.minio_cli.presigned_get_object(
            self.bucket_name,
            task.download_object,
            expires=datetime.timedelta(days=1)
        )

    def get_task_by_id(self, project, user, taskid):
        task = Task(taskid=taskid, project=project, user=user)

        self.create_bucket_if_not_exists()
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

        self.create_bucket_if_not_exists()
        return self.minio_cli.put_object(
            self.bucket_name, task.status_object,
            buf, len(data),
            content_type='application/json'
        )

    def upload_file(self, task: TaskStatus, buffer, filetype):
        # task.update = str(datetime.datetime.now())
        # data = task.to_json().encode('utf8')
        buf = io.BytesIO(buffer)

        self.create_bucket_if_not_exists()
        return self.minio_cli.put_object(
            self.bucket_name, task.upload_object,
            buf, len(buffer),
            content_type=mimetypes.types_map[filetype]
        )
