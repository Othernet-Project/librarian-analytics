import os
import hashlib

from squery_pg import Database


class DBContainer(object):
    """
    ``migrations`` is a package which contains the database migrations.

    ``conf`` argument is a dictionary of application options that are passed to
    the migrations.

    Actual name of the database will be the database name with
    '_test_<random_string>' suffix.
    """

    MAX_POOL_SIZE = 1  # This can only be 1 so gevent doesn't get used

    def __init__(self, dbname, migrations=None, conf={}, host='localhost',
                 port=5432, user='postgres', password=None):
        self.name = dbname
        self.conf = conf
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.databases = {}
        self.migrations = {}
        self.add_database(dbname, migrations)

    def add_database(self, dbname, migrations=None):
        real_dbname = random_name('test_{}'.format(dbname))
        self.databases[dbname] = {
            'name': real_dbname,
            'db': Database.connect(database=real_dbname,
                                   host=self.host,
                                   port=self.port,
                                   user=self.user,
                                   password=self.password,
                                   maxsize=self.MAX_POOL_SIZE),
        }
        self.migrations[dbname] = migrations

    def load_fixtures(self, table, data):
        """
        Load fixtures from ``data`` iterable into specified table. The data is
        epxeced to be an iterable of dicts.
        """
        name = self.name
        db = self.databases[name]['db']
        db.execute('BEGIN')
        for row in data:
            columns = row.keys()
            q = db.Insert(table, cols=columns)
            db.execute(q, row)
        db.execute('COMMIT')

    def setup(self):
        name = self.name
        db = self.databases[name]['db']
        db.recreate()
        db.migrate(db, self.migrations[name], self.conf)

    def teardown(self):
        db = self.databases[self.name]
        dbname = db['name']
        dbobj = db['db']
        dbobj.close()
        Database.drop(
            host=self.host,
            port=self.port,
            dbname=dbname,
            user=self.user,
            password=self.password,
            maxsize=self.MAX_POOL_SIZE)

    def __getattr__(self, name):
        try:
            return self.databases[name]['db']
        except KeyError:
            return object.__getattr__(self, name)


def random_name(prefix='test'):
    """
    Return random name that can be used to create the test database.
    """
    rndbytes = os.urandom(8)
    md5 = hashlib.md5()
    md5.update(rndbytes)
    return '{}_{}'.format(prefix, md5.hexdigest()[:7])
