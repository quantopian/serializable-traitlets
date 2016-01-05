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
def pg_required_kwargs():
    return {
        'username': 'user',
        'hostname': 'localhost',
        'database': 'db',
    }


@pytest.fixture
def pg_optional_kwargs():
    return {
        'port': 5432,
        'password': 'password',
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


def test_postgres_config_required(pg_required_kwargs, roundtrip_func):
    cfg = PostgresConfig(**pg_required_kwargs)
    check_attributes(
        cfg,
        merge(pg_required_kwargs, {'port': None, 'password': None}),
    )
    assert cfg.url == "postgres://user@localhost/db"
    rounded = roundtrip_func(cfg)
    assert_serializables_equal(cfg, rounded)
    assert rounded.url == cfg.url

    assert_serializables_equal(cfg, PostgresConfig.from_url(cfg.url))


def test_postgres_config_optional(pg_required_kwargs,
                                  pg_optional_kwargs,
                                  roundtrip_func):
    kwargs = merge(pg_required_kwargs, pg_optional_kwargs)
    cfg = PostgresConfig(**kwargs)
    check_attributes(cfg, kwargs)
    assert cfg.url == "postgres://user:password@localhost:5432/db"

    rounded = roundtrip_func(cfg)
    assert_serializables_equal(cfg, rounded)
    assert rounded.url == cfg.url

    assert_serializables_equal(cfg, PostgresConfig.from_url(cfg.url))


def test_all_pg_kwargs_required(pg_required_kwargs):

    kwargs = pg_required_kwargs.copy()
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
