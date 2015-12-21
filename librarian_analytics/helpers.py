import uuid
try:
    from io import BytesIO as StringIO
except ImportError:
    from cStringIO import StringIO

from bottle_utils.lazy import caching_lazy

from .bitstream import hex_to_bytes
from .data import generate_device_id, StatBitStream


ANALYTICS_TABLE = 'stats'


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


def get_stats(db):
    query = db.Select(sets=ANALYTICS_TABLE, where='sent = false')
    return db.fetchall(query)


def save_stats(db, data):
    query = db.Insert(ANALYTICS_TABLE, cols=data.keys())
    return db.execute(query, data)


def mark_sent_stats(db, stats):
    ids = [item['id'] for item in stats]
    query = db.Update(ANALYTICS_TABLE, where=db.sqlin('id', ids), sent=True)
    return db.execute(query, ids)


class AnalyticsDumper(object):

    def __init__(self, supervisor):
        self.supervisor = supervisor
        self._stats = None

    def _serialize_device_id(self):
        device_id_file = self.supervisor.config['analytics.device_id_file']
        device_id = prepare_device_id(device_id_file)
        return hex_to_bytes(uuid.UUID(str(device_id), version=4).hex)

    def to_string(self, mark_sent=False):
        # fetch only unsent entries
        db = self.supervisor.exts.databases.analytics
        self._stats = get_stats(db)
        if self._stats:
            device_id = self._serialize_device_id()
            serialized_data = device_id + StatBitStream.to_bytes(self._stats)
            if mark_sent:
                mark_sent_stats(db, self._stats)
            return serialized_data

    def to_file(self, mark_sent=False):
        dump = self.to_string(mark_sent=mark_sent)
        fd = StringIO()
        if dump:
            fd.write(dump)
            fd.seek(0)
        return fd

    def mark_sent(self):
        if self._stats:
            db = self.supervisor.exts.databases.analytics
            mark_sent_stats(db, self._stats)
