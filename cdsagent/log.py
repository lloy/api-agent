import logging
from logging import handlers as loghandlers

from cdsagent.cfg import CONF

__author__ = 'hardy.Zheng'


DEAFAULT_SIGN = ','
LOG_LEVEL = {
    '0': logging.DEBUG,
    '1': logging.INFO,
    '2': logging.WARNING,
    '3': logging.ERROR,
    '4': logging.CRITICAL}


class Logger(object):

    def __init__(self, name, level, path, max_bytes, back_count):
        self.level = LOG_LEVEL.get(level) if level else logging.INFO
        self.formatter = '%(asctime)s %(process)d %(name)s:%(lineno)d[%(levelname)s]:\t%(message)s'
        self.datefmt = '%a, %d %b %Y %H:%M:%S'
        self.filename = path
        self.filemode = 'w'
        self.max_bytes = max_bytes
        self.back_count = back_count
        self.logger = logging.getLogger(name)
        self.logger.setLevel(self.level)

        # file
        fh = logging.FileHandler(self.filename)
        # fh.setLevel(self.level)
        formatter = logging.Formatter(self.formatter)
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)

        # rotating
        rotating = loghandlers.RotatingFileHandler(
            self.filename,
            maxBytes=self.max_bytes,
            backupCount=self.back_count
            )
        # rotating.setLevel(self.level)
        formatter = logging.Formatter(self.formatter)
        rotating.setFormatter(formatter)
        self.logger.addHandler(rotating)

    def setup(self):
        pass

logger = Logger(
    "cdsagent",
    CONF.log.level,
    CONF.log.path,
    int(CONF.log.max_bytes),
    int(CONF.log.back_count))
LOG = logger.logger
