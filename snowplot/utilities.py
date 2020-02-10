import logging
import coloredlogs
import inspect
import sys

__version__ = '0.1.0'

def get_logger(name, level='DEBUG', ext_logger=None):
    """
    retrieves a logger with colored logs installed

    Args:
        name: string used to describe logger names
        level: log level to use
        ext_logger: External logger object, if not create a new one.

    Returns:
        log: instance of a logger with coloredlogs installed
    """

    fmt = fmt='%(name)s %(levelname)s %(message)s'
    if ext_logger == None:
        log = logging.getLogger(name)
    else:
        log = ext_logger

    coloredlogs.install(fmt=fmt,level=level, logger=log)
    return log

def getConfigHeader():
    """
    Generates string for inicheck to add to config files
    Returns:
        cfg_str: string for cfg headers
    """

    cfg_str = ("Config File for SnowPlot {0}\n"
              "For more SnowPlot related help see:\n"
              "{1}").format(__version__,'http://snowplot.readthedocs.io/en/latest/')
    return cfg_str
