from snowplot.profiles import *
from . import data_dir
import pytest
from os.path import join

class TestHandHardnessProfile():
    @pytest.fixture()
    def profile(self):
        filename = join(data_dir, 'hand_hardness.txt')
        return HandHardnessProfile(filename=filename, plot_id=0)

    @pytest.mark.parametrize("letter_value, numeric", [
        ('F-', 1),
        ('F+', 3),
        ('I', 16)
    ])
    def test_attribute_scale(self, profile, letter_value, numeric):
        """
        Test that the scale is being set correctly
        """
        assert profile.scale[letter_value] == numeric
