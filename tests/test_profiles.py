from snowplot.profiles import *
import pytest
from os.path import join, dirname, isfile
from inicheck.tools import get_user_config
import os


class TestHandHardnessProfile:
    section = 'hand_hardness'

    @pytest.fixture
    def config(self, cfg_dict):
        s = f'[{self.section}]\n'
        for k, v in cfg_dict.items():
            s += f'{k}: {v}\n'
        f = join(dirname(__file__), 'config.ini')
        s += '[output]\n'
        with open(f, mode='w+') as fp:
            fp.write(s)
        ucfg = get_user_config(f, modules=['snowplot'])
        yield ucfg.cfg[self.section]
        if isfile(f):
            os.remove(f)

    @pytest.fixture()
    def profile(self, data_dir, config):

        filename = join(data_dir, 'hand_hardness.txt')
        config['filename'] = filename
        return HandHardnessProfile(**config)

    @pytest.mark.parametrize("cfg_dict, letter_value, numeric", [
        ({}, 'F-', 1),
        ({}, 'F+', 3),
        # ('I', 16)
    ])
    def test_attribute_scale(self, profile, cfg_dict, letter_value, numeric):
        """
        Test that the scale is being set correctly
        """
        assert profile.scale[letter_value] == numeric


class TestGrainSizeProfile:
    section = 'grain_size'

    @pytest.fixture()
    def config(self, cfg_dict):
        s = f'[{self.section}]\n'
        for k, v in cfg_dict.items():
            s += f'{k}: {v}\n'
        f = join(dirname(__file__), 'config.ini')
        s += '[output]\n'
        with open(f, mode='w+') as fp:
            fp.write(s)
        ucfg = get_user_config(f, modules=['snowplot'])
        yield ucfg.cfg[self.section]
        if isfile(f):
            os.remove(f)

    @pytest.fixture()
    def profile(self, data_dir, config):
        filename = join(data_dir, 'snowex_stratigraphy.csv')
        config['filename'] = filename
        return GrainSizeProfile(**config)

    @pytest.mark.parametrize('cfg_dict', [
        ({})
    ])
    def test_profile_read(self, profile, cfg_dict):
        profile.open()
        print(profile)
