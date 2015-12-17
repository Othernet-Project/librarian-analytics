import logging

from bottle import request

from .decorators import install_tracking_cookie
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


def routes(config):
    return (
        ('analytics:collect', collect_data,
         'POST', '/analytics/', dict(unlocked=True)),
    )
