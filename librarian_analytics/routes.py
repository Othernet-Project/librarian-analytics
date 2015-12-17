import logging

from bottle import request


def collect_data():
    path = request.params.get('path')
    ctype = request.params.get('type')
    logging.debug("'%s' opener used on '%s'", ctype, path)

    return 'OK'


def routes(config):
    return (
        ('analytics:collect', collect_data,
         'POST', '/analytics/', dict(unlocked=True)),
    )
