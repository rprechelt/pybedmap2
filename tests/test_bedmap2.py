import bedmap2


def test_bedmap2_version():
    """
    Check the bedmap2 version.
    """
    assert bedmap2.__version__ == "0.0.1"
