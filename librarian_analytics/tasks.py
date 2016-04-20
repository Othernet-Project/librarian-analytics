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


def send_analytics(supervisor, retry_attempt=0):
    # report sending might be disabled in config
    if not supervisor.config.get('analytics.send_reports', False):
        return
    # preliminary tests passed, attempt report sending
    device_id_file = supervisor.config['analytics.device_id_file']
    throttle = supervisor.config['analytics.throttle']
    db = exts.databases.analytics
    ids, payload = helpers.get_payload(db, device_id_file, throttle)
    server_url = supervisor.config['analytics.server_url']
    try:
        urllib2.urlopen(server_url, urllib.urlencode({'stream': payload}))
    except Exception:
        retry_delay = supervisor.config['analytics.retry_delay']
        max_retries = supervisor.config['analytics.max_retries']
        # in case report sending failed previously, check if we exceeded
        # the maximum number of retry attempts and if that's the case,
        # abort mission
        if retry_attempt + 1 >= max_retries:
            logging.error("Analytics data transmission failed %s times "
                          "in a row. It won't be retried again until the "
                          "next cycle.", max_retries)
            return
        logging.error("Analytics data transmission failed. Retrying in "
                      "%s seconds.", retry_delay)
        supervisor.exts.tasks.schedule(send_analytics,
                                       args=(supervisor, retry_attempt + 1),
                                       delay=retry_delay)
    else:
        helpers.clear_transmitted(db, ids)
        logging.info("Analytics data transmission complete.")


def cleanup_analytics(supervisor):
    db = exts.databases.analytics
    max_records = supervisor.config['analytics.max_records']
    rowcount = helpers.cleanup_stats(db, max_records)
    logging.info("Analytics cleanup deleted %s records.", rowcount)
