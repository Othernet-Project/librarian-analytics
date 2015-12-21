import logging

from bottle import request
from fdsend import send_file

from librarian_core.utils import utcnow

from .decorators import install_tracking_cookie
from .helpers import AnalyticsDumper
from .tasks import store_data


@install_tracking_cookie
def collect_data():
    data = dict(path=request.params.get('path'),
                action=request.params.get('type'),
                timezone=request.params.get('tz'))
    data.update(request.tracking_info)
    supervisor = request.app.supervisor
    supervisor.exts.tasks.schedule(store_data, args=(supervisor, data))
    logging.debug("'%s' opener used on '%s'", data['action'], data['path'])
    return 'OK'


def download_stats():
    dumper = AnalyticsDumper(request.app.supervisor)
    stats_fd = dumper.to_file(mark_sent=True)
    filename = '{}.stats'.format(utcnow().isoformat())
    return send_file(stats_fd, filename, attachment=True)


def routes(config):
    return (
        ('analytics:collect', collect_data,
         'POST', '/analytics/', dict(unlocked=True)),
        ('analytics:download', download_stats,
         'GET', '/analytics/', dict(unlocked=True)),
    )
