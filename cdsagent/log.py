import logging
from logging import handlers as loghandlers


__author__ = 'hardy.Zheng'


DEAFAULT_SIGN = ','
LOG_LEVEL = {
    '0': logging.DEBUG,
    '1': logging.INFO,
    '2': logging.WARNING,
    '3': logging.ERROR,
    '4': logging.CRITICAL}


class Logger(object):

    def __init__(self, name, level, path, handlers, max_bytes, back_count):
        self.level = LOG_LEVEL.get(level) if level else logging.INFO
        self.formatter = '%(asctime)s %(process)d %(name)s:%(lineno)d[%(levelname)s]:\t%(message)s'
        self.datefmt = '%a, %d %b %Y %H:%M:%S'
        self.filename = path
        self.filemode = 'w'
        self.max_bytes = max_bytes
        self.back_count = back_count
        self._handlers = handlers
        logging.basicConfig(level=self.level,
                            format=self.formatter,
                            datefmt=self.datefmt,
                            filename=self.filename,
                            filemode=self.filemode)
        self.logger = logging.getLogger(name)

    def set_handler(self):
        for h in self._handlers:
            if h == 'console':
                console = logging.StreamHandler()
                console.setLevel(self.level)
                formatter = logging.Formatter(self.formatter)
                console.setFormatter(formatter)
                self.logger.addHandler(console)
            if h == 'rotating':
                rotating = loghandlers.RotatingFileHandler(
                    self.filename,
                    maxBytes=self.max_bytes,
                    backupCount=self.back_count
                    )
                rotating.setLevel(self.level)
                formatter = logging.Formatter(self.formatter)
                rotating.setFormatter(formatter)
                self.logger.addHandler(rotating)

    def setup(self):
        self.set_handler()
        return self.logger
