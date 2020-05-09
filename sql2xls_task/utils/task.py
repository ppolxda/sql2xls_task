# -*- coding: utf-8 -*-
"""
@create: 2020-04-01 06:07:29.

@author: ppolxda

@desc: task
"""
import six
import uuid
import json
import datetime
# from minio import Minio


class EnumStatus(object):

    WAITTING = 'WAITTING'
    DOING = 'DOING'
    CANCEL = 'CANCEL'
    FINISH = 'FINISH'

    enum_list = [
        WAITTING,
        DOING,
        CANCEL,
        FINISH,
    ]

    @classmethod
    def is_invaild(cls, val):
        return val not in cls.enum_list


class Task(object):

    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.taskid = self.kwargs.get(
            'taskid', str(uuid.uuid1()).replace('-', '')
        )
        self.mode = self.kwargs.get('mode', 'null')
        self.create = self.kwargs.get('create', str(datetime.datetime.now()))
        self.update = self.kwargs.get('update', str(datetime.datetime.now()))
        self.sql = self.kwargs.get('sql', None)
        self.sql_url = self.kwargs.get('sql_url', None)
        self.sql_parames = self.kwargs.get('sql_parames', [])
        self.options = self.kwargs.get('options', [])
        # self.upload_url = self.kwargs.get('upload_url', '')
        # self.status_url = self.kwargs.get('status_url', '')
        self.user = self.kwargs.get('user', 0)
        self.project = self.kwargs.get('project', 'null')
        self.fname = self.kwargs.get('fname', '')
        self.memo = self.kwargs.get('memo', '')

    def to_dict(self):
        return {
            'taskid': self.taskid,
            'mode': self.mode,
            'create': self.create,
            'update': self.update,
            'sql': self.sql,
            'sql_url': self.sql_url,
            'sql_parames': self.sql_parames,
            'options': self.options,
            # 'upload_url': self.upload_url,
            # 'status_url': self.status_url,
            'user': self.user,
            'project': self.project,
            'fname': self.fname,
            'memo': self.memo,
        }

    @property
    def status_object(self):
        return 'status/{}/{}/{}.json'.format(
            self.project,
            self.user,
            self.taskid
        )

    @property
    def upload_object(self):
        if isinstance(self.create, six.string_types):
            create = datetime.datetime.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(self.create, datetime.datetime):
            create = self.create
        else:
            raise TypeError('create time invaild') 

        if self.fname:
            return 'files/{}/{}/{}.xls'.format(
                self.project,
                self.user,
                '_'.join([
                    self.fname,
                    create.strftime('%Y%m%dT%H%M%S'),
                    self.taskid[:8],
                ])
            )
        else:
            return 'files/{}/{}/{}.xls'.format(
                self.project,
                self.user,
                '_'.join([
                    self.taskid,
                    create.strftime('%Y%m%dT%H%M%S')
                ]),
            )

    @property
    def download_object(self):
        return self.upload_object

    # def gen_url(self):
    #     self.status_url = self.minio_cli.presigned_put_object(
    #         self.bucket_name,
    #         self.status_object,
    #         expires=datetime.timedelta(days=1)
    #     )

    #     self.upload_url = self.minio_cli.presigned_put_object(
    #         self.bucket_name,
    #         self.download_object,
    #         expires=datetime.timedelta(days=1)
    #     )

    def check(self):
        # TODO - sql format checker
        if not self.sql or not isinstance(self.sql, six.string_types):
            raise TypeError('sql invaild')

        sql_lower = self.sql.lower()
        if not sql_lower.startswith('select') or 'from' not in sql_lower:
            raise TypeError('sql not select')

        # TODO - sql_url format checker
        if not self.sql_url or not isinstance(self.sql_url, six.string_types):
            raise TypeError('sql_url invaild')

        # TODO - sql_url format checker
        if not self.options or not isinstance(self.options, list):
            raise TypeError('options invaild')

        # TODO - sql_url format checker
        if not self.project or not isinstance(self.project, six.string_types):
            raise TypeError('project invaild')

        # TODO - sql_url format checker
        if not self.user or not isinstance(self.user, six.string_types):
            raise TypeError('user invaild')

        if self.fname and \
            (not isinstance(self.fname, six.string_types) or
                self.fname.find('.') >= 0):
            raise TypeError('fname format invaild')

        for i in self.options:
            if 'field' not in i or not i['field'] \
                    or not isinstance(i['field'], str):
                raise TypeError('options field name invaild')

            if 'cnname' not in i or not i['cnname'] \
                    or not isinstance(i['cnname'], str):
                raise TypeError('options field cnname invaild')

            if 'options' not in i or not i['options'] \
                    or not isinstance(i['options'], dict):
                i['options'] = {}
                # raise TypeError('options field options invaild')

            # if 'dataType' not in i['options'] \
            #         or not i['options']['dataType'] \
            #         or not isinstance(i['options']['dataType'], str):
            #     raise TypeError('options field dataType invaild')

    def check_full(self):
        self.check()

        # # TODO - upload_url format checker
        # if not self.upload_url:
        #     raise TypeError('upload_url invaild')

        # # TODO - status_url format checker
        # if not self.status_url:
        #     raise TypeError('status_url invaild')

    def to_json(self):
        return json.dumps(self.to_dict())

    @staticmethod
    def from_json(data):
        data = json.loads(data)
        return Task(**data)


class TaskStatus(Task):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.process = self.kwargs.get('process', {})
        self.status = self.process.get('status', EnumStatus.WAITTING)
        self.error = self.process.get('error', '')
        self.text = self.process.get('text', '')
        # self.memo = self.kwargs.get('memo', '')

    def to_task_list(self):
        return {
            'taskid': self.taskid,
            'memo': self.memo,
            'error': self.error,
            'text': self.text,
            'status': self.status,
        }

    def to_dict(self):
        _dict = super().to_dict()
        _dict['process'] = {
            'status': self.status,
            'error': self.error,
            'text': self.text,
        }
        return _dict

    @staticmethod
    def from_json(data):
        data = json.loads(data)
        return TaskStatus(**data)
