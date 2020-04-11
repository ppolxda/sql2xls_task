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


class AppClient(object):

    def __init__(self, host, project=None, **sessions):
        if not host or \
            not isinstance(host, str) or \
                not (host.startswith('http://') or
                     host.startswith('https://')):
            raise TypeError('host invaild')

        if host[-1] == '/':
            host = host[:-1]

        self.host = host
        self.project = project
        self.sessions = sessions

    async def add_task_sync(self, user, sql_url, sql, sql_parames,
                            options, memo='', project=None, fname=None,
                            **kwargs):
        project = self.__get_project(project)
        url = self.host + '/export/task/{project}/{user}/add/sync'.format(
            project=project, user=user
        )

        data = {
            'sql': sql,
            'sql_url': sql_url,
            'sql_parames': sql_parames,
            'options': options,
            'memo': memo,
            'user': user,
            'fname': fname,
            'project': project,
        }

        task = Task(**data)
        task.check()

        async with aiohttp.ClientSession(**self.sessions) as session:
            async with session.post(url, json=data, **kwargs) as response:
                if response.status != 200:
                    raise WebHttpError(response.reason)
                return await response.json()

    async def add_task_async(self, user, sql_url, sql, sql_parames,
                             options, memo='', project=None, fname=None,
                             **kwargs):
        project = self.__get_project(project)
        url = self.host + '/export/task/{project}/{user}/add/async'.format(
            project=project, user=user
        )

        data = {
            'sql': sql,
            'sql_url': sql_url,
            'sql_parames': sql_parames,
            'options': options,
            'memo': memo,
            'user': user,
            'fname': fname,
            'project': project,
        }

        task = Task(**data)
        task.check()

        async with aiohttp.ClientSession(**self.sessions) as session:
            async with session.post(url, json=data, **kwargs) as response:
                if response.status != 200:
                    raise WebHttpError(response.reason)
                return await response.json()

    async def delete_task_all(self, user, project=None, **kwargs):
        project = self.__get_project(project)
        url = self.host + '/export/task/{project}/{user}/all'.format(
            project=project, user=user
        )

        async with aiohttp.ClientSession(**self.sessions) as session:
            async with session.delete(url, **kwargs) as response:
                if response.status != 200:
                    raise WebHttpError(response.reason)
                return await response.json()

    async def delete_task_one(self, user, taskid, project=None, **kwargs):
        project = self.__get_project(project)
        url = self.host + '/export/task/{project}/{user}/{taskid}'.format(
            project=project, user=user, taskid=taskid
        )

        async with aiohttp.ClientSession(**self.sessions) as session:
            async with session.delete(url, **kwargs) as response:
                if response.status != 200:
                    raise WebHttpError(response.reason)
                return await response.json()

    async def get_task_list(self, user, project=None, **kwargs):
        project = self.__get_project(project)
        url = self.host + '/export/task/{project}/{user}/list'.format(
            project=project, user=user
        )

        async with aiohttp.ClientSession(**self.sessions) as session:
            async with session.get(url, **kwargs) as response:
                if response.status != 200:
                    raise WebHttpError(response.reason)
                return await response.json()

    async def upload_file(self, url, buffer, filetype, **kwargs):
        async with aiohttp.ClientSession(**self.sessions) as session:
            async with session.put(url, data=buffer, **kwargs) as response:
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
