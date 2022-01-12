from snowplot.utilities import titlize
import pytest

@pytest.mark.parametrize('label, expected',[
    ('depth [cm]', 'Depth [cm]'),
    ('whoa (test) [cm]', 'Whoa (test) [cm]'),
    ('depth', 'Depth')
])
def test_titlize(label, expected):
    assert titlize(label) == expected
