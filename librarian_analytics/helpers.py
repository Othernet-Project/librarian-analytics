import itertools

import time
import uuid

from dateutil import parser
from psycopg2 import Binary
from bitpack.utils import hex_to_bytes
from bottle_utils.lazy import caching_lazy

from .data import generate_device_id, StatBitStream


ANALYTICS_TABLE = 'stats'


# DATABASE OPERATIONS


def prep(data):
    """
    Prepare row data for writing to database. Namely, the 'payload' column is
    marked as binary data.
    """
    data['payload'] = Binary(data['payload'])
    return data


def get_stats(db):
    query = db.Select(sets=ANALYTICS_TABLE, order='time')
    return db.fetchall(query)


def save_stats(db, data):
    prep(data)
    query = db.Insert(ANALYTICS_TABLE, cols=data.keys())
    return db.execute(query, data)


def clear_transmitted(db, ids):
    q = db.Delete(ANALYTICS_TABLE, where='id = %s')
    db.executemany(q, ((i,) for i in ids))


def get_stats_bitstream(db):
    stats = get_stats(db)
    if not stats:
        return [], b''
    unpacked = sum([StatBitStream(bytes(s['payload'])).deserialize()
                    for s in stats], [])
    bitstream = StatBitStream(unpacked).serialize()
    ids = (s['id'] for s in stats)
    return ids, bitstream


# DEVICE ID


@caching_lazy
def prepare_device_id(path):
    try:
        with open(path, 'r') as f:
            current_key = f.read()
    except IOError:
        current_key = ''
    if not current_key:
        # No key has been set yet
        current_key = generate_device_id()
        with open(path, 'w') as f:
            f.write(current_key)
    assert current_key != '', "'My dog ate it' is a poor excuse"
    return current_key


def serialized_device_id(path):
    device_id = prepare_device_id(path)
    return hex_to_bytes(uuid.UUID(str(device_id), version=4).hex)


# PAYLOAD


def get_payload(db, conf):
    ids, bitstream = get_stats_bitstream(db)
    device_id = serialized_device_id(conf)
    return ids, device_id + bitstream


# GENERAL HELPERS


def as_time(timestamp):
    """
    Return integer timestamp based on string timestamp.
    """
    dt = parser.parse(timestamp)
    return int(time.mktime(dt.timetuple()))


class counter:
    """
    Callable that merely counts the number of times it was called and returns
    ``True`` as long as the call count does not exceed the max count.

    Example:

        >>> c = counter(3)
        >>> c()  # call 1
        True
        >>> c()  # call 2
        True
        >>> c()  # call 3 (max)
        True
        >>> c()  # call 4
        False
        >>> c()  # call 5
        False

    """
    # FIXME: Move this into librarian utils

    def __init__(self, max=1000):
        self.max = max
        self.count = 0

    def __call__(self, *args, **kwargs):
        self.count += 1
        return self.count <= self.max


def batches(data, batch_size=1000):
    """
    Batches of ``batch_size`` items ceated from ``data`` iterable.
    """
    # FIXME: Move this into librarian utils
    data = iter(data)
    while True:
        batch = list(itertools.islice(data, batch_size))
        if not batch:
            break
        yield batch
