# yes

__author__ = 'Hardy.zheng'
__email__ = 'wei.zheng@yun-idc.com'


import MySQLdb
import logging
from MySQLdb import Error as MySqlError
#from DBUtils.PooledDB import PooledDB

from cdsagent import cfg
# from cdsagent import exc


CONF = cfg.CONF
LOG = logging.getLogger(__name__)


class _MysqlBase(object):
    def __init__(self):
        try:
            self.conn = self._conn()
            self.cur = None
            self.set()
        except MySQLdb.Error, e:
            LOG.error(str(e))

    def _conn(self):
        try:
            return MySQLdb.Connection(
                host=CONF.mysql.host,
                user=CONF.mysql.user,
                passwd=CONF.mysql.passwd,
                db=CONF.mysql.name,
                port=int(CONF.mysql.port))
        except MySQLdb.Error, e:
            LOG.error(str(e))
            return None

    def set(self):
        try:
            if self.conn:
                self.cur = self.conn.cursor()
        except MySQLdb.Error, e:
            self.conn = None
            self.cur = None
            LOG.error(str(e))

    def reconn(self):
        self.conn = self._conn()
        self.set()

    def refresh(self):
        self.clear()
        self.reconn()
        self.set()

    def clear(self):
        if self.cur:
            self.cur.close()
            self.cur = None
        if self.conn:
            self.conn.close()
            self.conn = None

    def runCommand(self, cmd):
        try:
            if not self.conn or not self.cur:
                raise MySqlError('Not Connect DB')
            self.cur.execute(cmd)
            return self.cur.fetchall()
        except Exception, e:
            LOG.debug(str(e))
            raise MySqlError(str(e))

    def _isfound(self, id):
        raise NotImplementedError('_MysqlBase _isfound Not Implemented')
