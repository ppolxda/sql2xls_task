# -*- coding: utf-8 -*-
"""
@create: 2020-04-01 07:43:16.

@author: ppolxda

@desc: config
"""
from pyopts import opts
from pyopts import FeildOption
# from pyopts import RootSettings
from .config import Settings as Settingsx


class Settings(Settingsx):

    ROOT_LOGGING = 'root.logging'
    ROOT_LOGGING_OPT = FeildOption(
        ROOT_LOGGING, 'string',
        # default='./config/logging/app/logging_00.ini',
        default=None,
        desc='logging path',
        help_desc='logging path',
        opt_short_name='-l',
        allow_none=True
    )

    ROOT_DISABLE_EXISTING_LOGGERS = 'root.disable_existing_loggers'
    ROOT_DISABLE_EXISTING_LOGGERS_OPT = FeildOption(
        ROOT_DISABLE_EXISTING_LOGGERS, 'bool',
        default=False,
        desc='disable existing loggers',
        help_desc='disable existing loggers',
        opt_short_name='-ld'
    )

    def __init__(self, name):
        super().__init__(name)
