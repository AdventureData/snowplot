import logging
import coloredlogs

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
