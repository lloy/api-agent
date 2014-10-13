# yes
import logging
import time
import datetime
import uuid
from cdsagent import cfg
from cdsagent import exc
from cdsagent.common.impl_mysql import _MysqlBase
# from cdsagent.common.VIServer import ESXi_Server

__author__ = 'Hardy.Zheng'
__email__ = 'wei.zheng@yun-idc.com'

LOG = logging.getLogger(__name__)
CONF = cfg.CONF

_TASKSTATUS = ['OK', 'PROCESSING', 'ERROR']
_INSTANCESTATUS = ['running', 'stop', 'error', 'deleteing', 'lanuching']
_IPSTATUS = {'alloc': 1, 'un_alloc': 0}


class Instance(object):

    tasks = CONF.mysql.tasks
    instances = CONF.mysql.instances
    iptable = CONF.mysql.iptable

    def found(self):
        pass

    def create(self):
        pass

    def list(self):
        pass

    def delete(self):
        pass

    def update(self):
        pass

    def alloc_ip(self):
        pass

    def free_ip(self):
        pass

    def _commit(self, cmd):
        self.conn.runCommand(cmd)
        self.conn.conn.commit()


class InstanceCreate(Instance):

    CREATE_CMD = "insert into instances (\
    instance_uuid,\
    task_id,\
    name,\
    ip,\
    status,\
    os_type,\
    username,\
    passwd,\
    template_type,\
    instance_type,\
    iaas_type,\
    customers,\
    is_alloc,\
    create_time,\
    online_time,\
    off_time) values(\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\
    \"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%d\",\"%s\",\"%s\",\"%s\")"
    TITLE = "instance-%s"
    DEFAULT_IAAS_TYPE = "vsphere"
    DEFAULT_CUSTOMERS = "1hao"
    DEFAULT_USERNAME = "test"
    DEFAULT_PASSWD = "123456"

    def __init__(self):
        self.conn = _MysqlBase()

    def get_processing_task(self):
        cmd = "select task_id, model_type, template_type, instances_num from %s \
                where status=\"%s\"" % (self.tasks, _TASKSTATUS[1])
        LOG.debug('get_processing_task cmd: %s' % cmd)
        tasks = self.conn.runCommand(cmd)
        if tasks:
            return tasks
        else:
            return None

    def _create_cmd(self, task_id, model_type, template_type):
        instance_uuid = str(uuid.uuid1())
        name = self.TITLE % instance_uuid
        ts = time.time()
        timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        ip = self.get_idle_ip()
        status = "OK"
        username = self.DEFAULT_USERNAME
        passwd = self.DEFAULT_PASSWD
        os_type = template_type
        instance_type = model_type
        iaas_type = self.DEFAULT_IAAS_TYPE
        customers = self.DEFAULT_CUSTOMERS
        is_alloc = 0
        create_time = online_time = off_time = timestamp
        return self.CREATE_CMD % (instance_uuid, task_id, name,
                                  ip,
                                  status,
                                  os_type,
                                  username,
                                  passwd,
                                  template_type,
                                  instance_type,
                                  iaas_type,
                                  customers,
                                  is_alloc,
                                  create_time,
                                  online_time,
                                  off_time), ip

    def get_idle_instances(self, num, task_id, model_type, template_type):
        cmd = "select instance_uuid, ip, name from %s where is_alloc=0 limit %d"\
              % (self.instances, num)
        LOG.debug("get_idle_instances cmd: %s" % cmd)
        instances = self.conn.runCommand(cmd)
        if not instances:
            raise exc.NotAllocInstance("Not instance alloc")
        return instances

    def alloc_instance(self, instance_uuid):
        cmd = "update %s set is_alloc=1 where instance_uuid=\"%s\""\
              % (self.instances, instance_uuid)
        self._commit(cmd)

    # test create Instances
    def __test_creat(self, instances_num, task_id, model_type, template_type):
        for i in range(0, instances_num):
            cmd, ip = self._create_cmd(task_id, model_type, template_type)
            self._commit(cmd)
            self.alloc_ip(ip)

    def create(self, task_id, model_type, template_type, instances_num):
        LOG.debug("model_type:%s, template_type:%s, instances_num:%d"
                  % (model_type, template_type, instances_num))
        # self.__test_creat(instances_num, task_id, model_type, template_type)
        for i in self.get_idle_instances(instances_num, task_id, model_type, template_type):
            LOG.debug("Create Instances cmd: %s" % str(i))
            self.alloc_instance(i[0])
            self.alloc_ip(i[1])

    def alloc_ip(self, ip):
        LOG.debug('alloc ip : %s' % ip)
        cmd = "update %s set is_alloc=1 where ipaddress=\"%s\"" % (self.iptable, ip.strip())
        self._commit(cmd)

    def get_idle_ip(self):
        cmd = "select ipaddress from %s where is_alloc=0" % (self.iptable)
        ips = self.conn.runCommand(cmd)
        if ips:
            LOG.debug("ipaddress: %s" % str(ips[0][0]))
            return ips[0][0]
        raise exc.NotAllocIp('Not used Ipaddress')

    def finish_task(self, task_id):
        cmd = "update %s set status=\"OK\" where task_id=\"%s\"" % (self.tasks, task_id)
        LOG.debug("finish task cmd: %s" % cmd)
        self._commit(cmd)

    def run(self):
        LOG.info('action: Create Instances')
        try:
            self.conn.refresh()
            processing_tasks = self.get_processing_task()

            if not processing_tasks:
                LOG.info('Not Create Instances task')
                return

            for task in processing_tasks:
                self.create(task[0], task[1], task[2], task[3])
                self.finish_task(task[0])
                LOG.debug('task: %s' % str(task))

        except Exception, e:
            LOG.error(str(e))


class InstanceDelete(Instance):

    def __init__(self):
        self.conn = _MysqlBase()

    DELETE_CMD = "delete from %s where instance_uuid=\"%s\""

    def get_instance_uuid(self):
        cmd = "select instance_uuid, ip from %s where status=\"deleting\""\
              % (self.instances)
        LOG.debug('DELETE_CMD: %s' % cmd)
        return self.conn.runCommand(cmd)

    def _instance_split(self, instance):
        return instance[0], instance[1]

    def free_ip(self, ip):
        LOG.debug('free ip : %s' % ip)
        cmd = "update %s set is_alloc=0 where ipaddress=\"%s\"" % (self.iptable, ip.strip())
        self._commit(cmd)

    def delete(self, instance):
        instance_uuid, ip = self._instance_split(instance)
        LOG.debug('Delete instance uuid: %s' % instance_uuid)
        LOG.debug('Delete instance ip: %s' % ip)
        cmd = self.DELETE_CMD % (self.instances, instance_uuid)
        self._commit(cmd)
        self.free_ip(ip)

    def run(self):
        LOG.debug('action: Delete Instances')
        try:
            LOG.debug("mysql conn %s" % self.conn.conn)
            self.conn.refresh()
            instances = self.get_instance_uuid()
            LOG.debug('instances: %s' % str(instances))
            if not instances:
                LOG.debug('Not deleteing status instances')
                return
            for ins in instances:
                self.delete(ins)
        except Exception, e:
            LOG.error("delete Instances error: %s" % str(e))


class InstanceWatchDog(Instance):
    # esxi = ESXi_Server()

    # def __init__(self):
        # self.esxi_cli = self.esxi.connect_server(
            # CONF.vsphere.host_ip,
            # CONF.vsphere.username,
            # CONF.vsphere.passwd)

    def watch_dog(self):
        pass

    def _set_status(self):
        pass

    def run(self):
        LOG.debug('run watch_dog')
        LOG.debug('vsphere host_ip: %s' % CONF.vsphere.host_ip)
        LOG.debug('vsphere username: %s' % CONF.vsphere.username)
        LOG.debug('vsphere passwd: %s' % CONF.vsphere.passwd)
