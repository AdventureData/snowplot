import shutil

from snowplot.snowplot import make_vertical_plot
from os.path import isfile, dirname, join, isdir
from inicheck.tools import get_user_config
from inicheck.output import generate_config
import shutil
import os
import pytest
from matplotlib.testing.compare import compare_images

class ConfiguredPlotBase:
    # Section to write to
    section = None
    gold_fig = None

    @pytest.fixture(scope='function')
    def config(self, cfg_dict):
        s = f'[{self.section}]\n'
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
    def gold(self, gold_dir):
        yield join(gold_dir, self.gold_fig)

    @pytest.fixture(scope='function')
    def output(self, output_dir):
        yield join(output_dir, 'figure.png')

        if isdir(output_dir):
            shutil.rmtree(output_dir)

    def test_figure(self, figure, output, gold):
        assert compare_images(output, gold, 1e-6) is None


@pytest.mark.parametrize('cfg_dict', [{'filename': './data/hand_hardness.txt'}])
class TestHandHardnessPlot(ConfiguredPlotBase):
    section = 'hand_hardness'
    gold_fig = 'single_hand_hardness.png'


@pytest.mark.parametrize('cfg_dict', [{'filename': './data/lyte_profile.csv',
                                       'calibration_coefficients': '-1.46799e-06, 0.01441, -50.765, 64700.4'}])
class TestLyteProbePlot(ConfiguredPlotBase):
    section = 'lyte_probe'
    gold_fig = 'single_lyte_profile.png'


@pytest.mark.parametrize('cfg_dict', [{'filename': './data/smp.pnt'}])
class TestSMPPlot(ConfiguredPlotBase):
    section = 'snow_micropen'
    gold_fig = 'single_smp_profile.png'
