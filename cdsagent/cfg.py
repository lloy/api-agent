
import ConfigParser
import os

from cdsagent import exc

__author__ = 'Hardy.zheng'


_DEFAULT_CONFIG = {
    'core': {
        'interval': 60},
    'log': {
        'handler': 'rotating',
        'path': '/var/log/cds/cdsagent.log',
        'max_bytes': 2*1024,
        'back_count': 10,
        'level': '0'},
    'mysql': {
        'host': 'localhost',
        'port': 3306,
        'user': 'admin',
        'passwd': '123456',
        'name': 'apicloud',
        'driver': 'driver',
        'tasks': 'tasks',
        'iptable': 'iptable',
        'instances': 'instances',
        'instancetype': 'instancetype',
        'template': 'templatetype',
        'iaas': 'iaas'},
    'vsphere': {
        'host_ip': '172.16.0.11',
        'username': 'root',
        'passwd': 'cds-china'},
    'instance_create': {
        'action': 'create',
        'interval': 5},
    'instance_delete': {
        'action': 'delete',
        'interval': 10},
    'watch_dog': {
        'action': 'watch',
        'interval': 7},
    }


class Section(object):

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def update(self, k, v):
        setattr(self, k, v)


class CoreSection(Section):

    name = 'core'

    def __init__(self):
        kw = _DEFAULT_CONFIG.get(self.name)
        super(CoreSection, self).__init__(**kw)


class LogSection(Section):

    name = 'log'

    def __init__(self):
        kw = _DEFAULT_CONFIG.get(self.name)
        super(LogSection, self).__init__(**kw)


class MysqlSection(Section):

    name = 'mysql'

    def __init__(self):
        kw = _DEFAULT_CONFIG.get(self.name)
        super(MysqlSection, self).__init__(**kw)


class VsphereSection(Section):

    name = 'vsphere'

    def __init__(self):
        kw = _DEFAULT_CONFIG.get(self.name)
        super(VsphereSection, self).__init__(**kw)


class InstanceCreateSection(Section):

    name = 'instance_create'

    def __init__(self):
        kw = _DEFAULT_CONFIG.get(self.name)
        super(InstanceCreateSection, self).__init__(**kw)


class InstanceDeleteSection(Section):

    name = 'instance_delete'

    def __init__(self):
        kw = _DEFAULT_CONFIG.get(self.name)
        super(InstanceDeleteSection, self).__init__(**kw)


class WatchDogSection(Section):

    name = 'watch_dog'

    def __init__(self):
        kw = _DEFAULT_CONFIG.get(self.name)
        super(WatchDogSection, self).__init__(**kw)


class Factory():
    def get_section(self, name):
        sections = {
            'core': lambda: CoreSection(),
            'log': lambda: LogSection(),
            'vsphere': lambda: VsphereSection(),
            'instance_create': lambda: InstanceCreateSection(),
            'instance_delete': lambda: InstanceDeleteSection(),
            'watch_dog': lambda: WatchDogSection(),
            'mysql': lambda: MysqlSection()}
        return sections[name]()


class Config():

    f = Factory()

    def __init__(self):
        keys = _DEFAULT_CONFIG.keys()
        for k in keys:
            setattr(self, k, Config.f.get_section(k))

    def _is_exists(self, config_file):
        if not os.path.exists(config_file):
            return False
        else:
            return True

    def __call__(self, config_file):
        try:
            if not self._is_exists(config_file):
                raise exc.NotFoundConfigureFile('Not Found config file')
            conf = ConfigParser.ConfigParser()
            conf.read(config_file)
            for k in conf.sections():
                p = getattr(self, k, None)
                if not p:
                    setattr(self, k, Config.f.get_section(k))
                options = conf.options(k)
                for option in options:
                    p.update(option, conf.get(k, option))
        except Exception, e:
            raise e


def reload_config(config_file):
    conf = Config()
    return conf(config_file)

CONF = Config()
