from __future__ import absolute_import

from operator import itemgetter

import click

from straitlets import MultipleTraitErrors
from traitlets import TraitError


def _indent(msg):
    return '\n'.join('  ' + line for line in msg.splitlines())


class _ConfigFile(click.File):
    def __init__(self, config_type, encoding=None):
        super(_ConfigFile, self).__init__(
            mode='r',
            encoding=None,
            errors='strict',
            lazy=False,
            atomic=False,
        )
        self.config = config_type

    def read(self, f):  # pragma: no cover
        raise NotImplementedError('read')

    @property
    def name(self):  # pragma: no cover
        raise NotImplementedError('name')

    def convert(self, value, param, ctx):
        f = super(_ConfigFile, self).convert(value, param, ctx)
        try:
            return self.read(f)
        except MultipleTraitErrors as e:
            self.fail(
                'Failed to validate the schema:\n\n' + '\n'.join(
                    '%s:\n%s' % (key, _indent(str(err)))
                    for key, err in sorted(e.errors.items(), key=itemgetter(0))
                ),
                param,
                ctx,
            )
        except TraitError as e:
            self.fail(
                'Failed to validate the schema:\n%s' % _indent(str(e)),
                param,
                ctx,
            )


class JsonConfigFile(_ConfigFile):
    """A click parameter type for reading a :class:`~straitlets.Serializable`
    object out of json file.

    Parameters
    ----------
    config_type : type[Serializable]
        A subclass of :class:`~straitlets.Serializable`.

    Notes
    -----
    Normal :class:`~straitlets.Serializable` are not eagerly validated, if you
    want to check the schema of the file at read time you should use a
    :class:`~straitlets.StrictSerializable`.
    """
    name = 'JSON-FILE'

    def read(self, f):
        return self.config.from_json(f.read())


class YamlConfigFile(_ConfigFile):
    """A click parameter type for reading a :class:`~straitlets.Serializable`
    object out of yaml file.

    Parameters
    ----------
    config_type : type[Serializable]
        A subclass of :class:`~straitlets.Serializable`.

    Notes
    -----
    Normal :class:`~straitlets.Serializable` are not eagerly validated, if you
    want to check the schema of the file at read time you should use a
    :class:`~straitlets.StrictSerializable`.
    """
    name = 'YAML-FILE'

    def read(self, f):
        return self.config.from_yaml(f)
