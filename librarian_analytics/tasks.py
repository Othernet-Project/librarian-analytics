import logging
import urllib
import urllib2

from librarian_core.utils import utcnow

from .helpers import save_stats, AnalyticsDumper


def store_data(supervisor, data):
    data['timestamp'] = utcnow()
    save_stats(supervisor.exts.databases.analytics, data)
    logging.debug("Data stored for user_id: %s", data['user_id'])


def send_analytics(supervisor):
    if not supervisor.config.get('analytics.send_reports', False):
        return

    dumper = AnalyticsDumper(supervisor)
    query = {'stream': dumper.to_string(mark_sent=False)}
    server_url = supervisor.config['analytics.server_url']
    urllib2.urlopen(server_url, urllib.urlencode(query))
    # mark sent entries only if sending was successful
    dumper.mark_sent()
    logging.debug("Analytics data transmission complete.")
