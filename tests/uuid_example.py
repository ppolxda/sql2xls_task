# -*- coding: utf-8 -*-

import uuid
import functools


g_last_result = {}


def uuid_test(key, uuid_obj):
    result = str(uuid_obj())
    last_result = g_last_result.get(key, '')
    print('key[{}]:uuid[{}]:cmp[{}]:last[{}]'.format(
        key, result, last_result == result, last_result))
    g_last_result[key] = result


for i in range(10):
    print('-------------------------------------------')
    uuid_test('uuid1', uuid.uuid1)
    uuid_test('uuid3', functools.partial(
        uuid.uuid3, uuid.NAMESPACE_DNS, 'name'))
    uuid_test('uuid4', uuid.uuid4)
    uuid_test('uuid5', functools.partial(
        uuid.uuid5, uuid.NAMESPACE_DNS, 'name'))
