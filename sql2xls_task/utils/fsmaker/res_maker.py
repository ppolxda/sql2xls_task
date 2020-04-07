# -*- coding: utf-8 -*-
"""
@create: 2020-04-01 06:07:29.

@author: ppolxda

@desc: task
"""
import io
import six
import uuid
import json
import logging
import datetime
import mimetypes
from minio import Minio
from minio.error import NoSuchKey
from minio.error import ResponseError
from minio.error import NoSuchBucketPolicy


class ResourcesMaker(object):

    def __init__(self, minio_cli: Minio,
                 bucket_name: str, bucket_location: str,
                 trycount: int, expires: int,
                 logger: logging.Logger):
        if not isinstance(expires, six.integer_types) or \
                expires <= 0:
            expires = 15

        if not isinstance(trycount, six.integer_types) or \
                trycount <= 0:
            trycount = 5

        self.logger = logger
        self.minio_cli = minio_cli
        self.bucket_name = bucket_name
        self.bucket_location = bucket_location
        self.trycount = trycount
        self.expires = expires
        self.is_bucket_create = False

    def create_bucket_if_not_exists(self):
        if self.is_bucket_create:
            return

        result = self.minio_cli.bucket_exists(self.bucket_name)
        if not result:
            self.minio_cli.make_bucket(self.bucket_name, self.bucket_location)

        try:
            policy = self.minio_cli.get_bucket_policy(self.bucket_name)
        except NoSuchBucketPolicy as ex:
            policy = {
                'Version': '2012-10-17'
            }
        else:
            policy = json.loads(policy)

        policy_read_only = {
            "Version": policy['Version'],
            "Statement": [
                {
                    "Sid": "",
                    "Effect": "Allow",
                    "Principal": {"AWS": "*"},
                    "Action": "s3:GetBucketLocation",
                    "Resource": "arn:aws:s3:::{}".format(self.bucket_name)
                },
                {
                    "Sid": "",
                    "Effect": "Allow",
                    "Principal": {"AWS": "*"},
                    "Action": "s3:ListBucket",
                    "Resource": "arn:aws:s3:::{}".format(self.bucket_name)
                },
                {
                    "Sid": "",
                    "Effect": "Allow",
                    "Principal": {"AWS": "*"},
                    "Action": "s3:GetObject",
                    "Resource": "arn:aws:s3:::{}/*".format(self.bucket_name)
                }
            ]
        }

        self.minio_cli.set_bucket_policy(
            self.bucket_name, json.dumps(policy_read_only)
        )
        self.is_bucket_create = True

    def is_file_exist(self, path):
        try:
            self.create_bucket_if_not_exists()
            return self.minio_cli.stat_object(
                self.bucket_name, path,
            )
        except NoSuchKey:
            return None
        except ResponseError:
            return None

    def gen_object_path_str(self, project, suffix, trycount=0):
        if not project or not isinstance(project, six.string_types):
            raise TypeError('project invaild')

        if not suffix or \
            not isinstance(suffix, six.string_types) or \
                suffix[0] != '.':
            raise TypeError('suffix invaild')

        if not mimetypes.types_map.get(suffix, None):
            raise TypeError('suffix invaild')

        if trycount % 2 == 0:
            iuuid = str(uuid.uuid1()).replace('-', '')
        else:
            iuuid = str(uuid.uuid4()).replace('-', '')

        today = datetime.date.today()
        return '{project}/{year}/{month}/{iuuid}{suffix}'.format(
            project=project,
            year=today.year,
            month=today.month,
            iuuid=iuuid,
            suffix=suffix
        )

    def gen_object_path(self, project, suffix, trycount=0):
        if trycount > self.trycount:
            raise TypeError('gen_object_path error')

        _path = self.gen_object_path_str(project, suffix, trycount)
        if self.is_file_exist(_path):
            return self.gen_object_path(project, suffix, trycount + 1)
        return _path

    def presigned_put_object(self, project, suffix, expires=0):
        if expires <= 0:
            expires = self.expires

        path = self.gen_object_path(project, suffix)

        self.create_bucket_if_not_exists()
        return self.minio_cli.presigned_put_object(
            self.bucket_name, path,
            expires=datetime.timedelta(minutes=expires)
        )

    # def presigned_get_object(self, project, path, expires=60):
    #     return self.minio_cli.presigned_get_object(
    #         self.bucket_name, path,
    #         expires=datetime.timedelta(minutes=expires)
    #     )