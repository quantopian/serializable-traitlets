"""
Built-In Serializables
"""
from six.moves.urllib.parse import urlencode, urlparse
from traitlets import TraitError, validate

from .serializable import StrictSerializable
from .traits import Bool, Integer, List, Unicode, Dict


def join_filter_empty(sep, *elems):
    """
    Join a sequence of elements by ``sep``, filtering out empty elements.

    Example
    -------
    >>> join_filter_empty(':', 'a', None, 'c')
    'a:c'
    >>> join_filter_empty(':', 'a', None)
    'a'
    """
    return sep.join(map(str, filter(None, elems)))


class PostgresConfig(StrictSerializable):
    """
    Configuration for a PostgreSQL connection.
    """
    username = Unicode(help="Username for postgres login")
    password = Unicode(
        allow_none=True,
        default_value=None,
        help="Password for postgres login",
    )
    hostname = Unicode(
        allow_none=True,
        default_value=None,
        help="Postgres server hostname",
    )
    port = Integer(
        allow_none=True,
        default_value=None,
        help="Postgres server port",
    )

    @validate('port')
    def _port_requires_hostname(self, proposal):
        value = proposal['value']
        if value is not None and self.hostname is None:
            raise TraitError("Received port %s but no hostname." % value)
        return value

    database = Unicode(help="Database name")

    @property
    def netloc(self):
        user_pass = join_filter_empty(':', self.username, self.password)
        host_port = join_filter_empty(':', self.hostname, self.port)
        return '@'.join([user_pass, host_port])

    query_params = Dict(
        default_value={},
        help="Connection parameters",
    )

    @property
    def url(self):
        return join_filter_empty(
            '?',
            "postgresql://{netloc}/{db}".format(
                netloc=self.netloc,
                db=self.database,
            ),
            urlencode(self.query_params),
        )

    @classmethod
    def from_url(cls, url):
        """
        Construct a PostgresConfig from a URL.
        """
        parsed = urlparse(url)
        return cls(
            username=parsed.username,
            password=parsed.password,
            hostname=parsed.hostname,
            port=parsed.port,
            database=parsed.path.lstrip('/'),
            # Like parse_qs, but produces a scalar per key, instead of a list:
            query_params=dict(param.split('=')
                              for param in parsed.query.split('&'))
            if parsed.query else {},
        )


class MongoConfig(StrictSerializable):
    """
    Configuration for a MongoDB connection.
    """
    username = Unicode(
        allow_none=True,
        default_value=None,
        help="Username for Database Authentication",
    )

    password = Unicode(
        allow_none=True,
        default_value=None,
        help="Password for Database Authentication",
    )

    @validate('username')
    def _user_requires_password(self, proposal):
        new = proposal['value']
        # Must supply both or neither.
        if new and not self.password:
            raise TraitError("Username '%s' supplied without password." % new)
        return new

    @validate('password')
    def _password_requires_user(self, proposal):
        # Must supply both or neither.
        new = proposal['value']
        if new and not self.username:
            # Intentionally not printing a password here.
            raise TraitError("Password supplied without username.")
        return new

    hosts = List(
        trait=Unicode(),
        minlen=1,
        help=(
            "List of hosts in the replicaset.  "
            "To specify a port, postfix with :{portnum}."
        )
    )
    database = Unicode(help="Database Name")
    replicaset = Unicode(
        default_value=None,
        help="Replicaset Name",
        allow_none=True,
    )
    slave_ok = Bool(
        default_value=True,
        help="Okay to connect to non-primary?",
    )
    prefer_secondary = Bool(
        default_value=True,
        help="Prefer to connect to non-primary?",
    )
    ssl = Bool(default_value=False, help="Connect via SSL?")
    ssl_ca_certs = Unicode(
        allow_none=True,
        default_value=None,
        help="Path to concatenated CA certificates.",
    )
