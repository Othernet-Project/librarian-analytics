import logging
try:
    from io import StringIO
except ImportError:
    from StringIO import StringIO

from bottle import request
from fdsend import send_file

from librarian_core.utils import utcnow
from librarian_core.exts import ext_container as exts

from .decorators import install_tracking_cookie
from .helpers import get_payload
from .tasks import store_data


@install_tracking_cookie
def collect_data():
    data = dict(path=request.params.get('path'),
                action=request.params.get('type'),
                timezone=float(request.params.get('tz')))
    data.update(request.tracking_info)
    supervisor = request.app.supervisor
    supervisor.exts.tasks.schedule(store_data, args=(supervisor, data))
    logging.debug("'%s' opener used on '%s'", data['action'], data['path'])
    return 'OK'


def download_stats():
    supervisor = request.app.supervisor
    device_id_file = supervisor.conf['analytics.device_id_file']
    db = exts.databases.analytics
    _, payload = get_payload(db, device_id_file)
    filename = '{}.stats'.format(utcnow().isoformat())
    return send_file(StringIO(payload), filename, attachment=True)


def routes(config):
    return (
        ('analytics:collect', collect_data,
         'POST', '/analytics/', dict(unlocked=True)),
        ('analytics:download', download_stats,
         'GET', '/analytics/', dict(unlocked=True)),
    )
