import sys
from collections import OrderedDict
from os import mkdir
from os.path import join, isdir, dirname

from inicheck.output import generate_config, print_config_report
from inicheck.tools import check_config, get_checkers, get_user_config

# required for inicheck
import snowplot.utilities
import snowplot.profiles
import snowplot.plotting

"""Main module."""


def make_vertical_plot(config_file):
    """
    Main function in snowplot to interpret config files and piece together the
    plot users describe in the config file

    Args:
        config_file: config file in .ini format and can be checked with inicheck
    """
    # Get the cfg
    log = snowplot.utilities.get_logger("snowplot")
    ucfg = get_user_config(config_file, modules='snowplot', cli=True)
    warnings, errors = check_config(ucfg)
    print(warnings, errors)
    print_config_report(warnings, errors)
    if len(errors) > 0:
        print("Errors in config file. Check report above.")
        sys.exit()

    # outut a config file
    out = ucfg.cfg['output']['output_dir']

    if not isdir(out):
        mkdir(out)
    generate_config(ucfg, join(out, 'config_full.ini'))

    # Grab a copy of the config dictionary
    cfg = ucfg.cfg
    data = {}

    # gather all the templates for creating profiles
    profile_classes = get_checkers(module='snowplot.profiles',
                                   keywords='profile')

    # Create a map of the class names to the config names
    requested_profiles = OrderedDict()
    for v in cfg.keys():
        if v not in snowplot.__non_data_sections__:
            k = v.replace('_', '').lower()
            requested_profiles[k] = v

    # Create the profile objects and prerpare to add them to the figure
    for profile_name, cls in profile_classes.items():

        if profile_name in requested_profiles.keys():
            name = requested_profiles[profile_name]
            log.info("Building {} profile".format(name))
            # Add it to the dictionary of data
            data[profile_name] = cls(**cfg[name])

    # Build the final figure
    snowplot.plotting.build_figure(data, cfg)
