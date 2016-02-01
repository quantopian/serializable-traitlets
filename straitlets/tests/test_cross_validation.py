import pytest

from straitlets import Serializable, Unicode
from traitlets import validate, TraitError


class SomeConfig(Serializable):
    username = Unicode(allow_none=True).example('username')
    password = Unicode(allow_none=True).example('password')

    @validate('username', 'password')
    def _both_or_neither(self, proposal):
        new_value = proposal['value']
        name = proposal['trait'].name
        other_name = {
            'username': 'password',
            'password': 'username',
        }[name]
        other_value = getattr(self, other_name)
        if new_value is not None and other_value is None:
            raise TraitError("%s supplied without %s" % (name, other_name))
        if new_value is None and other_value is not None:
            raise TraitError("%s supplied without %s" % (other_name, name))
        return new_value


def test_example_instance():
    example = SomeConfig.example_instance()
    assert example.username == 'username'
    assert example.password == 'password'


def test_both_or_neither():
    cfg = SomeConfig(username='u', password='p')
    assert cfg.username == 'u'
    assert cfg.password == 'p'

    cfg = SomeConfig(username=None, password=None)
    assert cfg.username is None
    assert cfg.password is None

    with pytest.raises(TraitError):
        SomeConfig(username='username', password=None)

    with pytest.raises(TraitError):
        SomeConfig(username=None, password='password')
