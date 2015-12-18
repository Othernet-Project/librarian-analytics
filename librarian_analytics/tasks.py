import logging
import urllib
import urllib2
import uuid

from librarian_core.utils import utcnow

from .bitstream import hex_to_bytes
from .data import StatBitStream
from .decorators import prepare_device_id


ANALYTICS_TABLE = 'stats'


def store_data(supervisor, data):
    db = supervisor.exts.databases.analytics
    data['timestamp'] = utcnow()
    q = db.Insert(ANALYTICS_TABLE, cols=data.keys())
    db.execute(q, data)
    logging.debug("Data stored for user_id: %s", data['user_id'])


class SendAnalyticsTask(object):

    def __init__(self, supervisor):
        self.supervisor = supervisor
        return self._run()

    def _serialize_device_id(self):
        device_id_file = self.supervisor.config['analytics.device_id_file']
        device_id = prepare_device_id(device_id_file)
        return hex_to_bytes(uuid.UUID(str(device_id), version=4).hex)

    def _serialize(self, data):
        device_id = self._serialize_device_id()
        return device_id + StatBitStream.to_bytes(data)

    def _send(self, data):
        query = {'stream': data}
        server_url = self.supervisor.config['analytics.server_url']
        # no exception handling is performed here, because the background task
        # runner catches and logs all of them anyway, and caller of ``_send``
        # should not mark entries as sent if it was unsuccessful, so the
        # exception should propagate
        urllib2.urlopen(server_url, urllib.urlencode(query))
        logging.debug("Analytics data transmission complete.")

    def _run(self):
        # fetch only unsent entries
        db = self.supervisor.exts.databases.analytics
        q = db.Select(sets=ANALYTICS_TABLE, where='sent = false')
        data = db.fetchall(q)
        if data:
            serialized_data = self._serialize(data)
            self._send(serialized_data)
            # update sent flag on all entries
            sent_ids = [item['id'] for item in data]
            q = db.Update(ANALYTICS_TABLE,
                          where=db.sqlin('id', sent_ids),
                          sent=True)
            db.execute(q, sent_ids)
