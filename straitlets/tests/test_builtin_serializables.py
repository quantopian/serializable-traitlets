from __future__ import unicode_literals

import pytest

from traitlets import TraitError

from straitlets.utils import merge
from straitlets.test_utils import (
    assert_serializables_equal,
    check_attributes,
    multifixture,
    removed_keys,
    assert_urls_equal,
)

from ..builtin_models import MongoConfig, PostgresConfig


@pytest.fixture
def pg_required_kwargs():
    return {
        'username': 'user',
        'database': 'db',
    }


@pytest.fixture
def pg_optional_kwargs():
    return {
        'hostname': 'localhost',
        'port': 5432,
        'password': 'password',
        'query_params': {'connect_timeout': '10', 'sslmode': 'require'},
    }


@multifixture
def mongo_hosts_lists():
    yield ['web']
    yield ['web', 'scale']
    yield ['web:10421', 'scale:10474']


@pytest.fixture
def mongo_optional_kwargs():
    return {
        'replicaset': "secret_ingredient_in_the_webscale_sauce",
        'slave_ok': False,
        'prefer_secondary': False,
        'ssl': False,
        'ssl_ca_certs': '/path/to/ca_cert.pem'
    }


@pytest.fixture
def mongo_required_kwargs(mongo_hosts_lists):
    return {
        'username': 'user',
        'password': 'pass',
        'hosts': mongo_hosts_lists,
        'database': "webscale",
    }


def test_postgres_config_required(pg_required_kwargs, roundtrip_func):
    cfg = PostgresConfig(**pg_required_kwargs)
    check_attributes(
        cfg,
        merge(pg_required_kwargs, {'port': None, 'password': None}),
    )
    assert_urls_equal(cfg.url, "postgresql://user@/db")
    rounded = roundtrip_func(cfg)
    assert_serializables_equal(cfg, rounded, skip=['url'])
    assert_urls_equal(rounded.url, cfg.url)

    from_url = PostgresConfig.from_url(cfg.url)
    assert_serializables_equal(cfg, from_url, skip=['url'])
    assert_urls_equal(from_url.url, cfg.url)


def test_postgres_config_optional(pg_required_kwargs,
                                  pg_optional_kwargs,
                                  roundtrip_func):
    kwargs = merge(pg_required_kwargs, pg_optional_kwargs)
    cfg = PostgresConfig(**kwargs)
    check_attributes(cfg, kwargs)

    assert_urls_equal(
        cfg.url,
        "postgresql://user:password@localhost:5432/db?"
        "connect_timeout=10&sslmode=require")

    rounded = roundtrip_func(cfg)
    assert_serializables_equal(cfg, rounded)
    assert_urls_equal(rounded.url, cfg.url)

    from_url = PostgresConfig.from_url(cfg.url)
    assert_serializables_equal(cfg, from_url, skip=['url'])
    assert_urls_equal(from_url.url, cfg.url)


def test_all_pg_kwargs_required(pg_required_kwargs):

    kwargs = pg_required_kwargs.copy()
    for key in kwargs:
        with removed_keys(kwargs, [key]), pytest.raises(TraitError) as e:
            PostgresConfig(**kwargs)
        assert str(e.value).startswith('No default value found for %s' % key)


def test_pg_port_requires_hostname(pg_required_kwargs):

    # Hostname without port is ok.
    cfg = PostgresConfig(hostname='localhost', **pg_required_kwargs)
    check_attributes(
        cfg,
        merge(pg_required_kwargs, {'hostname': 'localhost'})
    )
    assert cfg.url == "postgresql://user@localhost/db"

    # Port without hostname is an error.
    with pytest.raises(TraitError) as e:
        PostgresConfig(port=5432, **pg_required_kwargs)
    assert str(e.value) == "Received port 5432 but no hostname."


def test_mongo_config(mongo_required_kwargs,
                      mongo_optional_kwargs,
                      roundtrip_func):

    with pytest.raises(TraitError):
        MongoConfig(**mongo_optional_kwargs)

    optional_kwarg_defaults = {
        'replicaset': None,
        'slave_ok': True,
        'prefer_secondary': True,
        'ssl': False,
        'ssl_ca_certs': None
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


def test_mongo_config_username_password_both_or_neither(mongo_required_kwargs):

    kwargs = mongo_required_kwargs.copy()

    with removed_keys(kwargs, ['username']), pytest.raises(TraitError) as e:
        MongoConfig(**kwargs)
    assert str(e.value) == "Password supplied without username."

    with removed_keys(kwargs, ['password']), pytest.raises(TraitError) as e:
        MongoConfig(**kwargs)
    assert str(e.value) == "Username 'user' supplied without password."

    with removed_keys(kwargs, ['username', 'password']):
        cfg = MongoConfig(**kwargs)

        check_attributes(
            cfg,
            merge(kwargs, {'username': None, 'password': None}),
        )
