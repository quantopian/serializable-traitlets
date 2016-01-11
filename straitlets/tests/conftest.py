import os
from ..test_utils import multifixture


def _roundtrip_to_dict(traited):
    return type(traited).from_dict(traited.to_dict())


def _roundtrip_to_json(traited):
    return type(traited).from_json(traited.to_json())


def _roundtrip_to_yaml(traited):
    return type(traited).from_yaml(traited.to_yaml())


def _roundtrip_to_base64(traited):
    return type(traited).from_base64(traited.to_base64())


def _roundtrip_to_environ_dict(traited):
    environ = {}
    traited.to_environ(environ)
    return type(traited).from_environ(environ)


def _roundtrip_to_os_environ(traited):
    environ = os.environ
    orig = dict(environ)

    traited.to_environ(environ)
    try:
        return type(traited).from_environ(environ)
    finally:
        environ.clear()
        environ.update(orig)


@multifixture
def roundtrip_func():
    yield _roundtrip_to_dict
    yield _roundtrip_to_json
    yield _roundtrip_to_yaml
    yield _roundtrip_to_base64
    yield _roundtrip_to_environ_dict
    yield _roundtrip_to_os_environ
