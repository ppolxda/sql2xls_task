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

    APP_HOST = 'app_config.app_host'
    APP_HOST_OPT = FeildOption(
        APP_HOST, 'string',
        default='0.0.0.0',
        desc='app_host',
        help_desc='app_host'
    )

    APP_PORT = 'app_config.app_port'
    APP_PORT_OPT = FeildOption(
        APP_PORT, 'int',
        default=22000,
        desc='app_port',
        help_desc='app_port'
    )

    def __init__(self, name):
        super().__init__(name)
        self.app_host = opts.get_opt(self.APP_HOST)
        self.app_port = opts.get_opt(self.APP_PORT)
