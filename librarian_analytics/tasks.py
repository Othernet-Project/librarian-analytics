import logging

from librarian_core.utils import utcnow


ANALYTICS_TABLE = 'analytics'


def store_data(supervisor, data):
    db = supervisor.exts.databases.analytics
    data['timestamp'] = utcnow()
    q = db.Insert(ANALYTICS_TABLE, cols=data.keys())
    db.execute(q, data)
    logging.debug("Data stored for user_id: %s", data['user_id'])


def send_collected_data(supervisor):
    db = supervisor.exts.databases.analytics
