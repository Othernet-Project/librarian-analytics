from ...data import StatBitStream
from ...helpers import batches


MKPAYLOAD = """
alter table stats rename to tmp;
create table stats
(
    id serial primary key,
    time timestamp not null,  -- makes it cheaper to sort
    payload bytea not null
);
"""


def converted(data):
    """
    Binary version of the analytics data. The binary version does not include
    the ``id`` and ``sent`` keys, but it does include everything else.
    """
    # Filter out id and sent keys because we don't need those.
    data = {k: v for k, v in data.items() if k not in ['id', 'sent']}
    return {
        'time': data['timestamp'],
        'payload': StatBitStream.to_bytes([data]),
    }


def up(db, conf):
    # We have a stats table where we stored raw data. We want to store the data
    # in a more compact form (binary string). We will stash the old table as
    # tmp and create a new one. Then we'll load the legacy data and reinsert
    # into the new table.
    db.executescript(MKPAYLOAD)
    q = db.Select('*', sets='tmp')
    old_data = db.fetchall(q)
    data = (converted(d) for d in old_data)
    for batch in batches(data):
        q = db.Insert('stats', cols=['time', 'payload'])
        db.executemany(q, batch)
    db.execute('DROP TABLE tmp;')
