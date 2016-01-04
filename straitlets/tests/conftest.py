from ..test_utils import multifixture


def _roundtrip_to_dict(traited):
    return type(traited).from_dict(traited.to_dict())


def _roundtrip_to_json(traited):
    return type(traited).from_json(traited.to_json())


def _roundtrip_to_yaml(traited):
    return type(traited).from_yaml(traited.to_yaml())


def _roundtrip_to_base64(traited):
    return type(traited).from_base64(traited.to_base64())


@multifixture
def roundtrip_func():
    yield _roundtrip_to_dict
    yield _roundtrip_to_json
    yield _roundtrip_to_yaml
    yield _roundtrip_to_base64
