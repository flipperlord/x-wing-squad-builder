import re
from x_wing_squad_builder.version import __version__


def test_version():

    version = __version__
    assert re.match(r'\d\.\d\.\d', version)
