import logging
import coloredlogs
import inspect
import sys
from inicheck.checkers import CheckType
from inicheck.utilities import is_valid

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

class CheckNumPlotLength(CheckType):
    """
    Check to see if the list provided is the same length as the number of plots
    being requested
    """

    def __init__(self, **kwargs):
        super(CheckNumPlotLength, self).__init__(**kwargs)
        self.context_value = kwargs['config'].cfg['plotting']['num_subplots']
        self.msg_level = "error"
        self.is_list = True
        self.is_pair = False

    def valid_length(self):
        """
        Checks to see if the length of the list is the same as the
        number of plots requested
        """
        valid = len(self.values) == self.context_value
        msg = None

        if not valid:
            if self.is_pair:
                valid = len(self.values) == 2 * self.context_value
                msg = "Must be a list of pairs the same length as subplots ({})".format(self.context_value)
            else:
                valid = len(self.values) == self.context_value
                msg = "Must be same length as number of subplots ({})".format(self.context_value)

        return valid,msg

    def is_valid(self, value):
        """
        Checks whether it convertable to datetime, then checks for order.

        Args:
            value: Single value to be evaluated

        Returns:
            tuple:
                **valid** - Boolean whether the value was acceptable
                **msg** - string to print if value is not valid.
        """
        valid, msg = is_valid(value, self.type_func, self.type)

        if valid:
            valid, msg = self.valid_length()

        return valid, msg

class CheckNumPlotLengthFloat(CheckNumPlotLength):
    """
    Check to see if the list provided is the same length as the number of plots
    being requested
    """
    def __init__(self, **kwargs):
        super(CheckNumPlotLengthFloat, self).__init__(**kwargs)
        self.type_func = float

class CheckNumPlotLengthFloatPair(CheckNumPlotLengthFloat):
    """
    Check to see if the list provided is the same length as the number of plots
    being requested
    """
    def __init__(self, **kwargs):
        super(CheckNumPlotLengthFloatPair, self).__init__(**kwargs)
        self.is_pair = True
