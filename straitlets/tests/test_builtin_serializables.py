from __future__ import unicode_literals

import pytest

from traitlets import TraitError

from straitlets.utils import merge
from straitlets.test_utils import (
    assert_serializables_equal,
    check_attributes,
    multifixture,
    removed_key,
)

from ..builtin_models import MongoConfig, PostgresConfig


@pytest.fixture
def pg_kwargs():
    return {
        'username': 'user',
        'password': 'pass',
        'hostname': 'localhost',
        'port': 5432,
        'database': 'db',
    }


@multifixture
def mongo_hosts_lists():
    yield ['web']
    yield ['web', 'scale']


@pytest.fixture
def mongo_optional_kwargs():
    return {
        'replicaset': "secret_ingredient_in_the_webscale_sauce",
        'slave_ok': False,
        'prefer_secondary': False,
        'ssl': False,
    }


@pytest.fixture
def mongo_required_kwargs(mongo_hosts_lists):
    return {
        'username': 'user ',
        'password': 'pass',
        'port': 666,
        'hosts': mongo_hosts_lists,
        'database': "webscale",
    }


def test_postgres_config(pg_kwargs, roundtrip_func):
    cfg = PostgresConfig(**pg_kwargs)
    check_attributes(cfg, pg_kwargs)
    assert cfg.url == "postgres://user:pass@localhost:5432/db"

    rounded = roundtrip_func(cfg)
    assert_serializables_equal(cfg, rounded)
    assert rounded.url == "postgres://user:pass@localhost:5432/db"


def test_all_pg_kwargs_required(pg_kwargs):

    kwargs = pg_kwargs.copy()
    for key in kwargs:
        with removed_key(kwargs, key), pytest.raises(TraitError) as e:
            PostgresConfig(strict=True, **kwargs)
        assert str(e.value).startswith('No default value found for %s' % key)


def test_mongo_config(mongo_required_kwargs,
                      mongo_optional_kwargs,
                      roundtrip_func):

    with pytest.raises(TraitError):
        MongoConfig(strict=True, **mongo_optional_kwargs)

    optional_kwarg_defaults = {
        'replicaset': None,
        'slave_ok': True,
        'prefer_secondary': True,
        'ssl': True,
    }

    without_optionals = MongoConfig(**mongo_required_kwargs)
    check_attributes(
        without_optionals,
        merge(mongo_required_kwargs, optional_kwarg_defaults),
    )
    assert_serializables_equal(
        without_optionals,
        roundtrip_func(without_optionals)
    )

    full_kwargs = merge(mongo_required_kwargs, mongo_optional_kwargs)
    with_optionals = MongoConfig(**full_kwargs)
    check_attributes(with_optionals, full_kwargs)
    assert_serializables_equal(with_optionals, roundtrip_func(with_optionals))
