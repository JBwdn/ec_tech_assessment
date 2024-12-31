"""
Unit tests for the package using pytest.

REF: <https://docs.pytest.org/en/7.4.x/>
"""


def test_imports():
    """Test that the package and a submodule can be imported."""

    import package  # pylint: disable=import-outside-toplevel

    assert package

    import package.scripts  # pylint: disable=import-outside-toplevel

    assert package.scripts
