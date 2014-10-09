import logging

from cdsagent import cfg
from cdsagent import exc
from cdsagent import service as os_service
from cdsagent import utils

__author__ = 'Hardy.zheng'


LOG = logging.getLogger(__name__)
_TASKS = ['instance_create', 'instance_delete']


class AgentManager(os_service.Service):

    def __init__(self):
        super(AgentManager, self).__init__()

    def start(self):
        LOG.info('start cdsagent....')
        for task in _TASKS:
            worker = getattr(cfg.CONF, task, None)
            if not worker:
                continue
            if not hasattr(worker, 'actions'):
                raise exc.NotSetPoller('not set poller in \
                    section configure file')

            try:
                LOG.debug('zhengwei %s' % str(worker.action))
                mgr = utils.get_manager(task, worker.action, False)

                if not hasattr(mgr.driver, 'run'):
                    raise exc.NotRunMethod('Not Found run() \
                            method in %s Poller' % task, '0000-003-01')

                interval = int(worker.interval)
                LOG.info('type: %s, interval:%d' % (task, interval))
                self.tg.add_timer(interval,
                                  self.interval_task,
                                  task=mgr.driver().run)
            except Exception, e:
                LOG.error('set %s Failed -->%s' % (task, str(e)))

    @staticmethod
    def interval_task(task):
        try:
            task()
        except Exception, e:
            LOG.error(str(e))
