import logging
import urllib
import urllib2

from librarian_core.utils import utcnow
from librarian_core.exts import ext_container as exts

from . import helpers
from .data import StatBitStream


def store_data(supervisor, data):
    data['timestamp'] = timestamp = utcnow()
    helpers.save_stats(exts.databases.analytics, {
        'time': timestamp,
        'payload': StatBitStream.to_bytes([data])
    })
    logging.debug("Data stored for user_id: %s", data['user_id'])


def send_analytics(supervisor):
    if not supervisor.config.get('analytics.send_reports', False):
        return
    device_id_file = supervisor.config['analytics.device_id_file']
    throttle = supervisor.config['analytics.throttle']
    db = exts.databases.analytics
    ids, payload = helpers.get_payload(db, device_id_file, throttle)
    server_url = supervisor.config['analytics.server_url']
    urllib2.urlopen(server_url, urllib.urlencode({'stream': payload}))
    helpers.clear_transmitted(db, ids)
    logging.debug("Analytics data transmission complete.")
