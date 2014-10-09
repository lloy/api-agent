# yes
"""Generic Node base class for all workers that run on hosts."""

import errno
import os
import signal
import sys
import logging


__author__ = 'Hardy.zheng'
__email__ = 'wei.zheng@yun-idc.com'

LOG = logging.getLogger(__name__)

try:
    # Importing just the symbol here because the io module does not
    # exist in Python 2.6.
    from io import UnsupportedOperation  # noqa
except ImportError:
    # Python 2.6
    UnsupportedOperation = None

from eventlet import event
from cdsagent import cfg

# from cdsagent import systemd
from cdsagent import threadgroup


CONF = cfg.CONF


def _sighup_supported():
    return hasattr(signal, 'SIGHUP')


def _is_daemon():
    # The process group for a foreground process will match the
    # process group of the controlling terminal. If those values do
    # not match, or ioctl() fails on the stdout file handle, we assume
    # the process is running in the background as a daemon.
    # http://www.gnu.org/software/bash/manual/bashref.html#Job-Control-Basics
    try:
        is_daemon = os.getpgrp() != os.tcgetpgrp(sys.stdout.fileno())
    except OSError as err:
        if err.errno == errno.ENOTTY:
            # Assume we are a daemon because there is no terminal.
            is_daemon = True
        else:
            raise
    except UnsupportedOperation:
        # Could not get the fileno for stdout, so we must be a daemon.
        is_daemon = True
    return is_daemon


def _is_sighup_and_daemon(signo):
    if not (_sighup_supported() and signo == signal.SIGHUP):
        # Avoid checking if we are a daemon, because the signal isn't
        # SIGHUP.
        return False
    return _is_daemon()


def _signo_to_signame(signo):
    signals = {signal.SIGTERM: 'SIGTERM',
               signal.SIGINT: 'SIGINT'}
    if _sighup_supported():
        signals[signal.SIGHUP] = 'SIGHUP'
    return signals[signo]


def _set_signals_handler(handler):
    signal.signal(signal.SIGTERM, handler)
    signal.signal(signal.SIGINT, handler)
    if _sighup_supported():
        signal.signal(signal.SIGHUP, handler)


class Launcher(object):
    """Launch one or more services and wait for them to complete."""

    def __init__(self):
        """Initialize the service launcher.

        :returns: None

        """
        self.services = Services()

    def launch_service(self, service):
        """Load and start the given service.

        :param service: The service you would like to start.
        :returns: None

        """
        self.services.add(service)

    def stop(self):
        """Stop all services which are currently running.

        :returns: None

        """
        self.services.stop()

    def wait(self):
        """Waits until all services have been stopped, and then returns.

        :returns: None

        """
        self.services.wait()

    def restart(self):
        """Reload config files and restart service.

        :returns: None

        """
        CONF.reload_config()
        self.services.restart()


class SignalExit(SystemExit):
    def __init__(self, signo, exccode=1):
        super(SignalExit, self).__init__(exccode)
        self.signo = signo


class ServiceLauncher(Launcher):
    def _handle_signal(self, signo, frame):
        # Allow the process to be killed again and die from natural causes
        _set_signals_handler(signal.SIG_DFL)
        raise SignalExit(signo)

    def handle_signal(self):
        _set_signals_handler(self._handle_signal)

    def _wait_for_exit_or_signal(self, ready_callback=None):
        status = None
        signo = 0

        LOG.info('Full set of CONF:')

        try:
            if ready_callback:
                ready_callback()
            super(ServiceLauncher, self).wait()
        except SignalExit as exc:
            signame = _signo_to_signame(exc.signo)
            LOG.info('Caught %s exiting' % (signame))
            status = exc.code
            signo = exc.signo
        except SystemExit as exc:
            status = exc.code
        finally:
            self.stop()

        return status, signo

    def wait(self, ready_callback=None):
        # systemd.notify_once()
        while True:
            self.handle_signal()
            status, signo = self._wait_for_exit_or_signal(ready_callback)
            if not _is_sighup_and_daemon(signo):
                return status
            self.restart()


class ServiceWrapper(object):
    def __init__(self, service, workers):
        self.service = service
        self.workers = workers
        self.children = set()
        self.forktimes = []


class Service(object):
    """Service object for binaries running on hosts."""

    def __init__(self, threads=1000):
        self.tg = threadgroup.ThreadGroup(threads)

        # signal that the service is done shutting itself down:
        self._done = event.Event()

    def reset(self):
        # NOTE(Fengqian): docs for Event.reset() recommend against using it
        self._done = event.Event()

    def start(self):
        pass

    def stop(self):
        self.tg.stop()
        self.tg.wait()
        # Signal that service cleanup is done:
        if not self._done.ready():
            self._done.send()

    def wait(self):
        self._done.wait()


class Services(object):

    def __init__(self):
        self.services = []
        self.tg = threadgroup.ThreadGroup()
        self.done = event.Event()

    def add(self, service):
        self.services.append(service)
        self.tg.add_thread(self.run_service, service, self.done)

    def stop(self):
        # wait for graceful shutdown of services:
        for service in self.services:
            service.stop()
            service.wait()

        # Each service has performed cleanup, now signal that the run_service
        # wrapper threads can now die:
        if not self.done.ready():
            self.done.send()

        # reap threads:
        self.tg.stop()

    def wait(self):
        self.tg.wait()

    def restart(self):
        self.stop()
        self.done = event.Event()
        for restart_service in self.services:
            restart_service.reset()
            self.tg.add_thread(self.run_service, restart_service, self.done)

    @staticmethod
    def run_service(service, done):
        """Service start wrapper.

        :param service: service to run
        :param done: event to wait on until a shutdown is triggered
        :returns: None

        """
        service.start()
        done.wait()


def launch(service):
    launcher = ServiceLauncher()
    launcher.launch_service(service)

    return launcher
