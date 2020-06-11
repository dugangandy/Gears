# -*- coding: utf-8 -*-
import codecs
import json
import os
import sys
import platform
import threading
from ConfigParser import RawConfigParser

import requests

__MUTEX = threading.RLock()

_ENV_CODE_EKEY = 'CONFIGENV'
_CONFIG_URL_EKEY = 'CONFIGURL'


class _Configuration(object):
    INSTANCE = None
    _IS_INIT = False
    _SERVER_MODE = True
    # _localDirecty='/data/webconfs/'
    _CONFIG_FILE_NAME = 'config.ini'

    def _ensure(self):
        if not self.__name:
            raise RuntimeError('must have name option in app section')

    def __init__(self, configParser):
        self.__configParser = configParser  # delegate
        self.__name = self.get('app', 'alias')
        self._ensure()
        self._try_apply_options(configParser)

    def appname(self):
        return self.__name

    def _try_apply_options(self, c):
        configModule = sys.modules[__name__]
        self.config = {}

        class DictObject(object):
            def __init__(self, items):
                self.__dict__.update(items)

        for sec in c.sections():
            setattr(configModule, str(sec), DictObject(dict(c.items(sec))))
            self.config[sec] = dict(c.items(sec))

    # TODO 最好是大小写不要敏感
    def get(self, section, name, default=None):
        '''
        section 必须大写(是个需要注意的地方)
        :param section:
        :param name:
        :param default:
        :return:
        '''
        config = self.__configParser
        if not config.has_option(section, name): return default
        return config.get(section, name)

    def getint(self, section, name, default=0):
        return int(self.get(section, name, default))

    def getfloat(self, section, name, default=0.0):
        return float(self.get(section, name, default))

    def getboolean(self, section, name, default='false'):
        value = self.get(section, name, default)
        return str(value).lower() == 'true'


def init(fname=_Configuration._CONFIG_FILE_NAME):
    if not _Configuration._IS_INIT:
        try:
            __MUTEX.acquire()
            if not _Configuration._IS_INIT:
                _init(fname)
        finally:
            __MUTEX.release()


def instance():
    if not _Configuration.INSTANCE:
        raise Exception("config not init")
    return _Configuration.INSTANCE


def appname():
    return instance().appname()


def get(section, name, default=None):
    return instance().get(section, name, default)


def getint(section, name, default=0):
    return instance().getint(section, name, default)


def getfloat(section, name, default=0.0):
    return instance().getfloat(section, name, default)


def getboolean(section, name, default=False):
    return instance().getboolean(section, name, default)


def injectConfig(config):
    if not isinstance(config, dict):
        raise TypeError('config should be dict type')
    for sec in instance().config:
        config.update(instance().config[sec])


def _init(fname):
    # _os_type = platform.system()
    _config_file = fname
    if not os.path.exists(_config_file):
        raise RuntimeError("unabled read config ,file not found")

    if _Configuration.INSTANCE: return _Configuration.INSTANCE
    try:
        __MUTEX.acquire()
        if _Configuration.INSTANCE: return _Configuration.INSTANCE
        configParser = RawConfigParser()
        configParser.optionxform = unicode
        if isinstance(_config_file, (str, unicode)):
            configParser.readfp(codecs.open(_config_file, "r", "utf-8"))
            _Configuration.INSTANCE = _Configuration(configParser)
            baseConfig = _BaseConfig(get("app", "alias"),
                                     get("config", "url"),
                                     get("config", "env"))
            localmode = getboolean("config", "localmode")
            if not localmode or _Configuration._SERVER_MODE:
                loader = Loader(baseConfig, configParser, _config_file)
                loader.loadAndSave()
                # reload config
                _Configuration.INSTANCE = _Configuration(configParser)
            _Configuration._IS_INIT = True
            return _Configuration.INSTANCE
    finally:
        __MUTEX.release()
    raise IOError(
        'read config file error,file name: %s server mode: %s' % (_config_file, str(_Configuration._SERVER_MODE)))


class _BaseConfig(object):
    def __init__(self,
                 systemAlias='unknow.systemalias',
                 configUrl='http://api.config.dugang.vip/service',
                 env='20'):
        self.systemAlias = systemAlias
        self.configUrl = os.environ.get(_CONFIG_URL_EKEY)
        if self.configUrl is None or self.configUrl == '':
            self.configUrl = configUrl
        self.env = os.environ.get(_ENV_CODE_EKEY)
        if self.env is None or self.env == '':
            _Configuration._SERVER_MODE = False
            self.env = env


class _ConfigFetcher(object):
    def __init__(self, baseUrl):
        if not isinstance(baseUrl, (str, unicode)):
            raise TypeError('baseUrl is bad type')
        if baseUrl is None or baseUrl == '':
            raise Exception('The baseUrl is null.')
        self.baseUrl = baseUrl

    def getRemoteProperties(self, systemAlias, environment):
        if systemAlias is None:
            raise Exception('The systemAlias is null.')
        if environment is None:
            raise Exception('The environment is null.')
        self.baseUrl = self.baseUrl.rstrip('/')
        url = self.baseUrl + '/snapshot/get-current'
        body = {
            'env': environment,
            'systemAlias': systemAlias
        }
        try:
            response = requests.post(url, json.dumps(body),
                                     headers={'content-type': 'application/json; charset=utf-8',
                                              'snapshot-password': '5e05773e-4359-40e3-9cbf-fc0333846aa2'},
                                     timeout=100)

            response.raise_for_status()
            data = response.json()
            if data['code'] == 0:
                if data['data'] is not None and data['data']['properties'] is not None:
                    return data['data']['properties']
            elif data['code'] == -13003:
                return []
            else:
                print 'Failed to get remote properties, message: ' + data['message']

        except requests.exceptions.ConnectionError as e:
            print e
        except requests.exceptions.ConnectTimeout as e:
            print e
        except requests.exceptions.Timeout as e:
            print e
        except requests.exceptions.RequestException as e:
            print e
        except Exception as e:
            print e
        return []


class _ConfigFileBuilder(object):
    def __init__(self, configFileName, configParser):
        if configFileName is None or configFileName == '':
            raise Exception('The configFileName is null.')
        if not isinstance(configParser, (RawConfigParser)):
            raise TypeError('configParser is bad type')
        self.configFileName = configFileName
        self.configParser = configParser

    def build(self, types):
        if types is not None:
            for type in types:
                if not self.configParser.has_section(type):
                    self.configParser.add_section(type)
                keyValues = types[type]
                for key in keyValues:
                    self.configParser.set(type, key, keyValues[key])
        file = codecs.open(self.configFileName, "w", "utf-8")
        write(self.configParser, file)
        file.close()


def write(configParser, fp):
    """Write an .ini-format representation of the configuration state."""
    if configParser._defaults:
        fp.write("[%s]\n" % configParser.DEFAULTSECT)
        for (key, value) in configParser._defaults.items():
            fp.write("%s = %s\n" % (key, unicode(value).replace('\n', '\n\t')))
        fp.write("\n")
    for section in configParser._sections:
        fp.write("[%s]\n" % section)
        for (key, value) in configParser._sections[section].items():
            if key == "__name__":
                continue
            if (value is not None) or (configParser._optcre == configParser.OPTCRE):
                key = " = ".join((key, unicode(value).replace('\n', '\n\t')))
            fp.write("%s\n" % (key))
        fp.write("\n")


class Loader(object):
    def __init__(self, config, configParser, configFileName):
        if not isinstance(config, (_BaseConfig)):
            raise TypeError('env is bad type')
        self.config = config
        self.configParser = configParser
        self.configFileName = configFileName

    def loadAndSave(self):
        baseConfig = self.config
        if baseConfig.systemAlias is None or baseConfig.systemAlias == '':
            raise Exception('Failed to get systemAlias !')
        if baseConfig.configUrl is None or baseConfig.configUrl == '':
            raise Exception('Failed to get configUrl !')
        if baseConfig.env is None or baseConfig.env == '':
            raise Exception('Failed to get env !')

        print 'BaseConfig: \n   systemAlias: %s\n   env: %s\n   servermode:%s\n   configUrl: %s\n   configFileName: %s' \
              % (baseConfig.systemAlias,
                 baseConfig.env,
                 _Configuration._SERVER_MODE,
                 baseConfig.configUrl,
                 self.configFileName)

        fetcher = _ConfigFetcher(baseConfig.configUrl)
        properties = fetcher.getRemoteProperties(
            baseConfig.systemAlias, baseConfig.env)
        types = {}
        for i, element in enumerate(properties):
            if not types.has_key(element['type']):
                types[element['type']] = {}
            types[element['type']][element['key']] = element['value']

        configFileBuilder = _ConfigFileBuilder(self.configFileName, self.configParser)
        configFileBuilder.build(types)
