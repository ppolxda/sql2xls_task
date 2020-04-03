# -*- coding: utf-8 -*-
"""
@create:2020-04-03 02:15:28.

@author: ppolxda

@desc: appclient
"""
import aiohttp
from .utils.task import Task


class WebHttpError(Exception):
    pass


class WebAppClient(object):

    def __init__(self, host, project=None):
        if not host or \
            not isinstance(host, str) or \
                not (host.startswith('http://') or host.startswith('https://')):
            raise TypeError('host invaild')

        if host[-1] == '/':
            host = host[:-1]

        self.host = host
        self.project = project

    async def add_task_sync(self, userid, sql, sql_url, sql_parames,
                            options, memo='', project=None):
        project = self.__get_project(project)
        url = self.host + '/export/task/{project}/{userid}/add/sync'.format(
            project=project, userid=userid
        )

        data = {
            'sql': sql,
            'sql_url': sql_url,
            'sql_parames': sql_parames,
            'options': options,
            'memo': memo,
        }

        task = Task(**data)
        task.check()

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data) as response:
                if response.status != 200:
                    raise WebHttpError(response.reason)
                return await response.json()

    async def add_task_async(self, userid, sql, sql_url, sql_parames,
                             options, memo='', project=None):
        project = self.__get_project(project)
        url = self.host + '/export/task/{project}/{userid}/add/async'.format(
            project=project, userid=userid
        )

        data = {
            'sql': sql,
            'sql_url': sql_url,
            'sql_parames': sql_parames,
            'options': options,
            'memo': memo,
        }

        task = Task(**data)
        task.check()

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data) as response:
                if response.status != 200:
                    raise WebHttpError(response.reason)
                return await response.json()

    async def delete_task_all(self, userid, project=None):
        project = self.__get_project(project)
        url = self.host + '/export/task/{project}/{userid}/all'.format(
            project=project, userid=userid
        )

        async with aiohttp.ClientSession() as session:
            async with session.delete(url) as response:
                if response.status != 200:
                    raise WebHttpError(response.reason)
                return await response.json()

    async def delete_task_one(self, userid, taskid, project=None):
        project = self.__get_project(project)
        url = self.host + '/export/task/{project}/{userid}/{taskid}'.format(
            project=project, userid=userid, taskid=taskid
        )

        async with aiohttp.ClientSession() as session:
            async with session.delete(url) as response:
                if response.status != 200:
                    raise WebHttpError(response.reason)
                return await response.json()

    async def get_task_list(self, userid, project=None):
        project = self.__get_project(project)
        url = self.host + '/export/task/{project}/{userid}/list'.format(
            project=project, userid=userid
        )

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    raise WebHttpError(response.reason)
                return await response.json()

    async def upload_file(self, url, buffer, filetype):
        async with aiohttp.ClientSession() as session:
            async with session.put(url, data=buffer) as response:
                if response.status == 200:
                    return

                html = await response.text()
                return html

    def __get_project(self, project=None):
        if project:
            return project

        if not self.project:
            raise TypeError('project not set')

        return self.project
