import pytest
from os.path import join, dirname


@pytest.fixture(scope='session')
def data_dir():
    return join(dirname(__file__),'data')

@pytest.fixture(scope='session')
def gold_dir(data_dir):
    return join(data_dir, 'gold')

@pytest.fixture(scope='session')
def output_dir():
    return join(dirname(__file__), 'output')
