# -*- coding: utf-8 -*-
"""
@create: 2020-04-01 06:09:25.

@author: ppolxda

@desc: broker
"""
from .task import Task
from .task import TaskStatus


class Broker(object):

    def push_task(self, task: Task):
        raise NotImplementedError

    def pop_task(self) -> TaskStatus:
        raise NotImplementedError
