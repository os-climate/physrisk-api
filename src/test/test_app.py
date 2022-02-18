from physrisk_api import server


def test_home():
    """Introductory test to setup CI. It will change."""

    assert server.home() == "Hello World !"
