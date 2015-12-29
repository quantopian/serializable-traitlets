"""
Testing utilities.
"""
import pytest


def multifixture(g):
    """
    Decorator for turning a generator into a "parameterized" fixture that emits
    the generated values.
    """
    fixture_values = list(g())

    @pytest.fixture(params=fixture_values)
    def _fixture(request):
        return request.param

    return _fixture
