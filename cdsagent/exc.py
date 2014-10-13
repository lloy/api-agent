
__author__ = 'Hardy.zheng'


class AgentException(Exception):

    def __init__(self, message, errno='0000-000-00'):
        self.msg = message
        self.code = errno
        super(AgentException, self).__init__(self.msg, self.code)


class ConfigureException(AgentException):

    """
    errno = 0000-001-00
    """

    def __init__(self, message, errno='0000-001-00'):
        super(ConfigureException, self).__init__(message, errno)


class NotSetPoller(ConfigureException):
    """
    errno = 0000-001-02
    """
    pass


class SetPollerError(Exception):
    pass


class NotRunMethod(AgentException):
    """
    errno = 0000-003-01
    """
    pass


class NotAllocInstance(Exception):
    pass


class EsxiNotConnect(Exception):
    pass


class NotFoundConfigureFile(ConfigureException):
    """
    errno = 0000-001-01
    """
    def __init__(self, message):
        errno = '0000-001-01'
        super(ConfigureException, self).__init__(message, errno)


class MultipleResultsFound(AgentException):
    pass


class NoResultFound(AgentException):
    pass


class BadAggregate(Exception):
    pass


class NotAllocIp(Exception):
    pass
