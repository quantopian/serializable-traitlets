"""
Built-In Serializables
"""
from .serializable import Serializable
from .traits import Bool, Integer, List, Unicode


class PostgresConfig(Serializable):
    """
    Configuration for a PostgreSQL connection.
    """
    username = Unicode(help="Username for postgres login")
    password = Unicode(help="Password for postgres login")
    hostname = Unicode(help="Postgres server hostname")
    port = Integer(help="Postgres server port")
    database = Unicode(help="Database name")

    @property
    def url(self):
        return "postgres://{username}:{password}@{host}:{port}/{db}".format(
            username=self.username,
            password=self.password,
            host=self.hostname,
            port=self.port,
            db=self.database,
        )


class MongoConfig(Serializable):
    """
    Configuration for a MongoDB connection.
    """
    username = Unicode(help="Username for Database Authentication")
    password = Unicode(help="Password for Database Authentication")
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
