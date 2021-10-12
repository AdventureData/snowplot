import pytest
from snowplot.profiles import HandHardnessProfile
from os.path import join, dirname

data_dir = join(dirname(__file__),'data')

@pytest.fixture()
def hand_hardness():
    filename = join('data', 'hand_hardness.txt')
    return HandHardnessProfile(filename=filename)
