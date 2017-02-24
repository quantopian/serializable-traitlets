import sys

from .to_primitive import to_primitive
from .traits import SerializableTrait

if sys.version_info.major < 3:
    # raise a more explicit error message if this is imported in Python 2
    raise ImportError('%s is only available in Python 3' % __name__)

# noqa on the import because it is not at the top of the module. We cannot
# import this module until we know that we are in Python 3.
import pathlib  # noqa


@to_primitive.register(pathlib.Path)
def _path_to_primitive(path):
    return str(path)


class Path(SerializableTrait):
    def validate(self, obj, value):
        # ``pathlib.Path`` is a nop when called on a ``pathlib.Path`` object
        return pathlib.Path(value)
