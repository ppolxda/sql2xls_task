# -*- coding: utf-8 -*-
"""
@create: 2020-04-01 07:43:16.

@author: ppolxda

@desc: config
"""
# import re
# import io
import redis
import logging
# import mimetypes
from minio import Minio
# from minio import PostPolicy
# from minio.error import ResponseError
from pyopts import opts
from pyopts import FeildOption
from pyopts import RootSettings
from .brokers.redis_broker import RedisBroker
from .fsmaker.task_maker import TaskMaker


class Settings(RootSettings):

    ROOT_LOGGING = 'root.logging'
    ROOT_LOGGING_OPT = FeildOption(
        ROOT_LOGGING, 'string',
        default='./config/logging/worker/logging_00.ini',
        desc='logging path',
        help_desc='logging path',
        opt_short_name='-l',
        allow_none=True
    )

    ROOT_CONFIG = 'root.config'
    ROOT_CONFIG_OPT = FeildOption(
        ROOT_CONFIG, 'string',
        default='file://./config/main.ini',
        desc='main config path',
        help_desc=(
            'main config path'
            '(file://./config/main.ini|etcd://localhost)'
        ),
        opt_short_name='-c',
        allow_none=True
    )

    BROKER_MODE = 'broker_config.broker_mode'
    BROKER_MODE_OPT = FeildOption(
        BROKER_MODE, 'string',
        default='redis',
        desc='broker_mode',
        help_desc='broker_mode'
    )

    DB_REDIS_URL = 'dbs_config.redis_url'
    DB_REDIS_URL_OPT = FeildOption(
        DB_REDIS_URL, 'string',
        default='redis://localhost:6379/0',
        desc='redis_url',
        help_desc='redis_url'
    )

    DB_MINIIO_URL = 'dbs_config.miniio_url'
    DB_MINIIO_URL_OPT = FeildOption(
        DB_MINIIO_URL, 'string',
        default='http://localhost:9000/',
        desc='miniio_url',
        help_desc='miniio_url'
    )

    DB_MINIIO_ACCESSKEY = 'dbs_config.miniio_accesskey'
    DB_MINIIO_ACCESSKEY_OPT = FeildOption(
        DB_MINIIO_ACCESSKEY, 'string',
        default='minioadmin',
        desc='miniio_accesskey',
        help_desc='miniio_accesskey'
    )

    DB_MINIIO_SECRETKEY = 'dbs_config.miniio_secretkey'
    DB_MINIIO_SECRETKEY_OPT = FeildOption(
        DB_MINIIO_SECRETKEY, 'string',
        default='minioadmin',
        desc='miniio_secretkey',
        help_desc='miniio_secretkey'
    )

    DB_MINIIO_BUCKET = 'dbs_config.miniio_bucket'
    DB_MINIIO_BUCKET_OPT = FeildOption(
        DB_MINIIO_BUCKET, 'string',
        default='filesxls',
        desc='miniio_bucket',
        help_desc='miniio_bucket'
    )

    DB_MINIIO_RES_BUCKET = 'dbs_config.miniio_res_bucket'
    DB_MINIIO_RES_BUCKET_OPT = FeildOption(
        DB_MINIIO_RES_BUCKET, 'string',
        default='filesres',
        desc='miniio_res_bucket',
        help_desc='miniio_res_bucket'
    )

    DB_MINIIO_REGION = 'dbs_config.miniio_region'
    DB_MINIIO_REGION_OPT = FeildOption(
        DB_MINIIO_REGION, 'string',
        default=None,
        desc='miniio_region',
        help_desc='miniio_region',
        allow_none=True
    )

    def __init__(self, name):
        self.init_opt(name)
        self.broker_mode = opts.get_opt(self.BROKER_MODE)
        self.redis_url = opts.get_opt(self.DB_REDIS_URL)
        self.miniio_url = opts.get_opt(self.DB_MINIIO_URL)
        self.miniio_accesskey = opts.get_opt(self.DB_MINIIO_ACCESSKEY)
        self.miniio_secretkey = opts.get_opt(self.DB_MINIIO_SECRETKEY)
        self.miniio_bucket = opts.get_opt(self.DB_MINIIO_BUCKET)
        self.miniio_res_bucket = opts.get_opt(self.DB_MINIIO_RES_BUCKET)
        self.miniio_region = opts.get_opt(self.DB_MINIIO_REGION)

        self.redis_cli = redis.Redis.from_url(self.redis_url)
        self.borker = RedisBroker(self.redis_cli)

        if self.miniio_url.endswith('/'):
            raise TypeError('miniio_url invaild, suffix error')

        if self.miniio_url.startswith('https://'):
            secure = True
            self.miniio_url = self.miniio_url[len('https://'):]
        else:
            secure = False
            self.miniio_url = self.miniio_url[len('http://') :]

        self.minio_cli = Minio(
            self.miniio_url,
            access_key=self.miniio_accesskey,
            secret_key=self.miniio_secretkey,
            # region=self.miniio_region,
            secure=secure,
        )

        self.task_maker = TaskMaker(
            self.borker, self.minio_cli,
            self.miniio_bucket, self.miniio_region,
            logging.getLogger('taskmaker')
        )
