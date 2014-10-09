from optparse import OptionParser

from cdsagent import service as os_service
from cdsagent.main import AgentManager
from cdsagent import cfg
from cdsagent import exc
from cdsagent.log import Logger


__author__ = 'Hardy.zheng'


parser = OptionParser()
parser.add_option("-c", "--config", dest="filename",
                  help="cds agent configure file",
                  metavar="FILE")


def run():
    os_service.launch(AgentManager()).wait()


def set_log(name):
    log_handlers = [h.strip() for h in cfg.CONF.log.handler.split(',')]
    logger = Logger(name,
                    cfg.CONF.log.level,
                    cfg.CONF.log.path,
                    log_handlers,
                    cfg.CONF.log.max_bytes,
                    cfg.CONF.log.back_count)
    return logger.setup()


def set_configure(filename):
    try:
        cfg._configure_file = filename
        cfg.CONF(filename)
    except exc.ConfigureException, e:
        raise e


if __name__ == '__main__':

    (options, args) = parser.parse_args()
    if not options.filename:
        parser.error("not input config file, --config filename")

    set_configure(options.filename)
    set_log('cds-agent')
    run()
