"""
Built-In Serializables
"""
from traitlets import TraitError

from .compat import urlparse
from .serializable import Serializable
from .traits import Bool, Integer, List, Unicode


class PostgresConfig(Serializable):
    """
    Configuration for a PostgreSQL connection.
    """
    username = Unicode(help="Username for postgres login")
    password = Unicode(
        allow_none=True,
        default_value=None,
        help="Password for postgres login",
    )
    hostname = Unicode(help="Postgres server hostname")
    port = Integer(
        allow_none=True,
        default_value=None,
        help="Postgres server port",
    )
    database = Unicode(help="Database name")

    @property
    def url(self):
        return "postgres://{username}{password}@{host}{port}/{db}".format(
            username=self.username,
            password=':' + self.password if self.password else '',
            host=self.hostname,
            port=':' + str(self.port) if self.port else '',
            db=self.database,
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
        )


class MongoConfig(Serializable):
    """
    Configuration for a MongoDB connection.
    """
    username = Unicode(
        allow_none=True,
        default_value=None,
        help="Username for Database Authentication",
    )

    def _username_changed(self, name, old, new):
        # Must supply both or neither.
        if new and not self.password:
            raise TraitError("Username '%s' supplied without password." % new)
        return new

    password = Unicode(
        allow_none=True,
        default_value=None,
        help="Password for Database Authentication",
    )

    def _password_changed(self, name, old, new):
        # Must supply both or neither.
        if new and not self.username:
            # Intentionally not printing a password here.
            raise TraitError("Password supplied without username.")
        return new

    hosts = List(
        Unicode,
        minlen=1,
        help="List of hosts in the replicaset",
    )
    port = Integer(
        help="Port on which the primary is running"
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
    ssl = Bool(default_value=True, help="Connect via SSL?")
