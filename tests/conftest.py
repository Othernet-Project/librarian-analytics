import os
import sys
import random
import datetime
from collections import namedtuple

import pytest
import psycopg2

import helpers as helpers_mod
from squery_pg.pytest_fixtures import *

from librarian_analytics import data


RANDOMCHARS = 'abcdefghijklmnopqrstuvwxyz0123456789'
py3 = sys.version >= (3, 0, 0)
BASETIME = datetime.datetime(2016, 5, 5, 12, 0, 0)
HOUR = 360

dbfixture = namedtuple('dbfixture', ['timestamp', 'data', 'payload', 'row'])


def random_ts():
    delta = random.randrange(-HOUR, HOUR, 1)
    return BASETIME + datetime.timedelta(seconds=delta)


def random_path_component():
    return ''.join(random.choice(RANDOMCHARS) for i in range(10))


def random_content_path():
    '/'.join(random_path_component() for i in range(random.randrange(1, 5)))


@pytest.fixture(scope='session')
def database_config():
    """
    Database configuration
    """
    return {
        'databases': [
            {'name': 'analytics',
             'migrations': 'librarian_analytics.migrations.analytics'}
        ],
        'conf': {},
    }


@pytest.yield_fixture
def random_path():
    """
    Random path to be used in testing file operations.
    """
    prefix = '/tmp/{}'
    filename = ''.join(random.choice(RANDOMCHARS) for i in range(12))
    path = prefix.format(filename)
    yield path
    if os.path.exists(path):
        os.unlink(path)


@pytest.fixture
def random_datapoint():
    """
    Factory for random analytics datapints. The returned data has the following
    attributes:

    - ``timestamp`` (seconds since UNIX epoch)
    - ``data`` (the unprocessed datapoint data)
    - ``payload`` (binary payload)
    - ``row`` (data to be inserted into the database row)
    """
    ts = random_ts()
    bitstream_data = {
        'user_id': data.generate_user_id(),
        'timestamp': ts,
        'timezone': 0,
        'path': random_content_path(),
        'action': random.choice(data.ACTIONS),
        'os_family': random.choice(data.OS_FAMILIES),
        'agent_type': random.choice(data.AGENT_TYPES),
    }
    payload = data.StatBitStream.to_bytes([bitstream_data])
    row = {
        'time': ts,
        'payload': psycopg2.Binary(payload)
    }
    return dbfixture(ts, bitstream_data, payload, row)


@pytest.fixture
def random_dataset():
    """
    Factory for random analytics datasets (returns generator object)
    """
    def _random_dataset(count=5):
        return (random_datapoint() for i in range(count))
    return _random_dataset


@pytest.fixture
def helpers():
    """
    An object with a number of helper methods.
    """
    return helpers_mod
