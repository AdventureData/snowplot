from snowplot.snowplot import make_vertical_plot
from os.path import isfile, dirname, join, isdir
from inicheck.tools import get_user_config
from inicheck.output import generate_config
import shutil
import os
import pytest
from matplotlib.testing.compare import compare_images


@pytest.mark.parametrize('section, cfg_dict, gold_fig', [
    # Test Hand hardness
    ('hand_hardness', {'filename': './data/hand_hardness.txt'}, 'single_hand_hardness.png'),
    ('hand_hardness', {'filename': './data/snowex_stratigraphy.csv'}, 'snowex_handhardness_profiles.png'),
    # Test lyte probe
    ('lyte_probe', {'filename': './data/lyte_profile.csv',
                    'calibration_coefficients': '-1.46799e-06, 0.01441, -50.765, 64700.4'},
     'single_lyte_profile.png'),
    # Test SMP
    ('snow_micropen', {'filename': './data/smp.pnt'}, 'single_smp_profile.png')
])
class TestMakeVerticalPlot:
    # Section to write to

    @pytest.fixture(scope='function')
    def config(self, cfg_dict, section):
        s = f'[{section}]\n'
        for k, v in cfg_dict.items():
            s += f'{k}: {v}\n'
        f = join(dirname(__file__), 'config.ini')
        s += '[output]\n'
        s += 'show_plot: False\n'
        s += 'dpi: 50\n'
        s += 'filename: figure.png\n'

        with open(f, mode='w+') as fp:
            fp.write(s)
        # Populate the config
        ucfg = get_user_config(f, modules=['snowplot'])
        # Write out the new config again
        generate_config(ucfg, f)
        yield f

        if isfile(f):
            os.remove(f)

    @pytest.fixture(scope='function')
    def figure(self, config, cfg_dict):
        make_vertical_plot(config)

    @pytest.fixture(scope='function')
    def gold(self, gold_dir, gold_fig):
        yield join(gold_dir, gold_fig)

    @pytest.fixture(scope='function')
    def output(self, output_dir):
        yield join(output_dir, 'figure.png')

        if isdir(output_dir):
            shutil.rmtree(output_dir)

    def test_figure(self, figure, output, gold):
        assert compare_images(output, gold, 1e-6) is None
