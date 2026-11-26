import rover


def test_rover_package_is_importable():
    assert rover.__name__ == "rover"


def test_rover_package_has_version():
    assert rover.__version__ == "0.1.0"
