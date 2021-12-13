"""Top-level package for snowplot."""

from os.path import abspath, dirname, join

from .utilities import getConfigHeader

# Inicheck attributes for config files
__core_config__ = abspath(join(dirname(__file__), 'master.ini'))
__recipes__ = abspath(join(dirname(__file__), 'recipes.ini'))
__config_titles__ = {
    "lyte_probe": "Lyte Probe data to plot and process",
    "snow_micropen": "SMP data to plot and process",
    "hand_hardness": "Hand Hardness data to plot and process",
    "output": " Outputting details for the final figure",
}
__config_header__ = getConfigHeader()
__config_checkers__ = 'utilities'

__author__ = """Micah Johnson"""
__email__ = 'micah.johnson150@gmail.com'
__version__ = '0.2.0'

__non_data_sections__ = ['output']
