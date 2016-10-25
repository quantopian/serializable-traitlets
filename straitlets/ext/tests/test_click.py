import re
from textwrap import dedent

import click
from click.testing import CliRunner
import pytest

from straitlets import (
    Serializable,
    StrictSerializable,
    Bool,
    Unicode,
    Integer,
)
from straitlets.ext.click import (
    JsonConfigFile,
    YamlConfigFile,
)
from straitlets.test_utils import assert_serializables_equal


@pytest.fixture
def runner():
    return CliRunner()


class Config(Serializable):
    bool = Bool()
    unicode = Unicode()
    int = Integer()


class MissingAttr(Serializable):
    bool = Bool()
    unicode = Unicode()


class StrictConfig(Config, StrictSerializable):
    pass


@pytest.fixture
def expected_instance():
    return Config(
        bool=True,
        unicode='ayy',
        int=1,
    )


@pytest.fixture
def missing_attr_instance():
    return MissingAttr(
        bool=True,
        unicode='ayy',
    )


multi_error_output = re.compile(
    dedent(
        """\
        ^Usage: main \[OPTIONS\]

        Error: Invalid value for "--config": Failed to validate the schema:

        bool:
          No default value found for bool trait of <.+?>
        int:
          No default value found for int trait of <.+?>
        unicode:
          No default value found for unicode trait of <.+?>
        $""",
    ),
)

single_error_output = re.compile(
    dedent(
        """\
        ^Usage: main \[OPTIONS\]

        Error: Invalid value for "--config": Failed to validate the schema:
          No default value found for int trait of <.+?>
        $""",
    ),
)


def test_json_file(runner, expected_instance):
    instance = [None]  # nonlocal

    @click.command()
    @click.option('--config', type=JsonConfigFile(Config))
    def main(config):
        instance[0] = config

    with runner.isolated_filesystem():
        with open('f.json', 'w') as f:
            f.write(expected_instance.to_json())

        result = runner.invoke(
            main,
            ['--config', 'f.json'],
            input='not-json',
            catch_exceptions=False,
        )
        assert result.output == ''
        assert result.exit_code == 0
        assert_serializables_equal(
            instance[0],
            expected_instance,
        )


def test_json_multiple_errors(runner):
    @click.command()
    @click.option('--config', type=JsonConfigFile(StrictConfig))
    def main(config):  # pragma: no cover
        pass

    with runner.isolated_filesystem():
        with open('f.json', 'w') as f:
            f.write('{}')

        result = runner.invoke(
            main,
            ['--config', 'f.json'],
            input='not-json',
            catch_exceptions=False,
        )
        assert result.exit_code
        assert multi_error_output.match(result.output)


def test_json_single_error(runner, missing_attr_instance):
    @click.command()
    @click.option('--config', type=JsonConfigFile(StrictConfig))
    def main(config):  # pragma: no cover
        pass

    with runner.isolated_filesystem():
        with open('f.json', 'w') as f:
            f.write(missing_attr_instance.to_json())

        result = runner.invoke(
            main,
            ['--config', 'f.json'],
            input='not-json',
            catch_exceptions=False,
        )
        assert result.exit_code
        assert single_error_output.match(result.output)


def test_yaml_file(runner, expected_instance):
    instance = [None]  # nonlocal

    @click.command()
    @click.option('--config', type=YamlConfigFile(Config))
    def main(config):
        instance[0] = config

    with runner.isolated_filesystem():
        with open('f.yml', 'w') as f:
            f.write(expected_instance.to_yaml())

        result = runner.invoke(
            main,
            ['--config', 'f.yml'],
            input='not-yaml',
            catch_exceptions=False,
        )
        assert result.output == ''
        assert result.exit_code == 0
        assert_serializables_equal(
            instance[0],
            expected_instance,
        )


def test_yaml_multiple_errors(runner):
    @click.command()
    @click.option('--config', type=YamlConfigFile(StrictConfig))
    def main(config):  # pragma: no cover
        pass

    with runner.isolated_filesystem():
        with open('f.yml', 'w') as f:
            f.write('{}')

        result = runner.invoke(
            main,
            ['--config', 'f.yml'],
            input='not-yaml',
            catch_exceptions=False,
        )
        assert result.exit_code
        assert multi_error_output.match(result.output)


def test_yaml_single_error(runner, missing_attr_instance):
    @click.command()
    @click.option('--config', type=YamlConfigFile(StrictConfig))
    def main(config):  # pragma: no cover
        pass

    with runner.isolated_filesystem():
        with open('f.yml', 'w') as f:
            f.write(missing_attr_instance.to_yaml())

        result = runner.invoke(
            main,
            ['--config', 'f.yml'],
            input='not-yaml',
            catch_exceptions=False,
        )
        assert result.exit_code
        assert single_error_output.match(result.output)
