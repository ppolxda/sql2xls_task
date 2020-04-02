# -*- coding: utf-8 -*-
"""
@create: 2020-04-01 06:09:25.

@author: ppolxda

@desc: redis_broker
"""
import redis
from ..broker import Task
from ..broker import TaskStatus
from ..broker import Broker


class RedisBroker(Broker):

    TAKS_KEY = 'export:tasks'

    def __init__(self, redis_cli: redis.Redis):
        self.redis_cli = redis_cli

    def push_task(self, task: Task):
        return self.redis_cli.rpush(self.TAKS_KEY, task.to_json())

    def pop_task(self) -> TaskStatus:
        task = self.redis_cli.lpop(self.TAKS_KEY)
        if not task:
            return None
        return TaskStatus.from_json(task)
