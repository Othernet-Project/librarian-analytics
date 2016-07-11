import logging
import urllib
import urllib2

from greentasks import Task

from librarian.core.utils import utcnow
from librarian.core.exts import ext_container as exts

from . import helpers
from .data import StatBitStream


def store_data(data):
    data['timestamp'] = timestamp = utcnow()
    helpers.save_stats(exts.databases.librarian, {
        'time': timestamp,
        'payload': StatBitStream.to_bytes([data])
    })
    logging.debug("Data stored for user_id: %s", data['user_id'])


class SendAnalytics(Task):
    name = 'send_analytics'
    periodic = True

    def get_start_delay(self):
        return exts.config['analytics.send_interval']

    def get_delay(self, previous_delay):
        return exts.config['analytics.send_interval']

    def get_retry_delay(self, previous_retry_delay, retry_count):
        retry_delay = exts.config['analytics.retry_delay']
        max_retries = exts.config['analytics.max_retries']
        # in case report sending failed previously, check if we exceeded
        # the maximum number of retry attempts and if that's the case,
        # abort mission
        if retry_count + 1 >= max_retries:
            logging.error("Analytics data transmission failed %s times "
                          "in a row. It won't be retried again until the "
                          "next cycle.", max_retries)
            return None
        logging.error("Analytics data transmission failed. Retrying in "
                      "%s seconds.", retry_delay)
        return retry_delay

    def run(self, retry_attempt=0):
        # report sending might be disabled in config
        if not exts.config.get('analytics.send_reports', False):
            return
        # preliminary tests passed, attempt report sending
        device_id_file = exts.config['analytics.device_id_file']
        throttle = exts.config['analytics.throttle']
        db = exts.databases.librarian
        ids, payload = helpers.get_payload(db, device_id_file, throttle)
        if not ids:
            # there are no unsent analytics stats, abort
            return
        server_url = exts.config['analytics.server_url']
        urllib2.urlopen(server_url, urllib.urlencode({'stream': payload}))
        helpers.clear_transmitted(db, ids)
        logging.info("Analytics data transmission complete.")


class CleanupAnalytics(Task):
    name = 'cleanup_analytics'
    periodic = True

    def get_start_delay(self):
        return exts.config['analytics.cleanup_interval']

    def get_delay(self, previous_delay):
        return exts.config['analytics.cleanup_interval']

    def run(self):
        db = exts.databases.librarian
        max_records = exts.config['analytics.max_records']
        rowcount = helpers.cleanup_stats(db, max_records)
        logging.info("Analytics cleanup deleted %s records.", rowcount)
