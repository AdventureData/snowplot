"""Top-level package for snowplot."""

from os.path import abspath, dirname, join
from .utilities import getConfigHeader

# Inicheck attributes for config files
__core_config__ = abspath(join(dirname(__file__), 'master.ini'))
__recipes__ = abspath(join(dirname(__file__),'recipes.ini'))
__config_titles__ = {
                    "Lyte Probe":"Lyte Probe data to plot and process",
                    "labeling":"Annotations to be added to the plot",
                    "output":" Outputting details for the final figure",
                    }
__config_header__ = getConfigHeader()
__config_checkers__ = 'utilities'

__author__ = """Micah Johnson"""
__email__ = 'micah.johnson150@gmail.com'
__version__ = '0.1.0'
