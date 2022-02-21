import logging
import coloredlogs

from inicheck.checkers import CheckType
from inicheck.utilities import is_valid
from inicheck.config import MasterConfig



__version__ = '0.2.0'


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

    fmt = fmt = '%(name)s %(levelname)s %(message)s'
    if ext_logger is None:
        log = logging.getLogger(name)
    else:
        log = ext_logger

    coloredlogs.install(fmt=fmt, level=level, logger=log)
    return log


def getConfigHeader():
    """
    Generates string for inicheck to add to config files
    Returns:
        cfg_str: string for cfg headers
    """

    cfg_str = ("Config File for SnowPlot {0}\n"
               "For more SnowPlot related help see:\n"
               "{1}").format(__version__, 'http://snowplot.readthedocs.io/en/latest/')
    return cfg_str


class CheckFloatPair(CheckType):
    """
    Check to see if the list provided is the same length as the number of plots
    being requested
    """

    def __init__(self, **kwargs):
        super(CheckFloatPair, self).__init__(**kwargs)
        self.msg_level = "error"
        self.is_list = True
        self.type_func = float

    def valid_length(self):
        """
        Checks to see if the length of the list is the same as the
        number of plots requested
        """
        valid = len(self.values) == 2
        msg = "Must be a list of pairs the same length as subplots ({})".format(
            2)


        return valid, msg

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

def get_encapsulated(str_line, encapsulator):
    """
    Returns items found in the encapsulator, useful for finding units

    Args:
        str_line: String that has encapusulated info we want removed
        encapsulator: string of characters encapusulating info to be removed
    Returns:
        result: list of strings found inside anything between encapsulators

    e.g.
        line = 'density (kg/m^3), temperature (C)'
        ['kg/m^3', 'C'] = get_encapsulated(line, '()')
    """

    result = []

    if len(encapsulator) > 2:
        raise ValueError('encapsulator can only be 1 or 2 chars long!')

    elif len(encapsulator) == 2:
        lcap = encapsulator[0]
        rcap = encapsulator[1]

    else:
        lcap = rcap = encapsulator

    # Split on the lcap
    if lcap in str_line:
        for i, val in enumerate(str_line.split(lcap)):
            # The first one will always be before our encapsulated
            if i != 0:
                if lcap != rcap:
                    result.append(val[0:val.index(rcap)])
                else:
                    result.append(val)

    return result


def titlize(label):
    """
    Upper case all things except things encapsulated in () or []
    """
    temp = label
    result = ''
    units = []
    encapsulators = []
    for encaps in ['()', '[]']:
        if encaps[0] in label:
            units.append(get_encapsulated(label, encaps)[0])
            encapsulators.append(encaps[0])

    for u in units:
        temp = temp.replace(u, '')

    temp = temp.title()

    for c, u in zip(encapsulators, units):
        if c in temp:
            temp = (c + u).join(temp.split(c))

    return temp

def get_profile_defaults(section, core_config):
    m = MasterConfig(core_config)
    defaults = {}
    for name,obj in m.cfg[section].items():
        defaults[name] = obj.default
    return defaults
