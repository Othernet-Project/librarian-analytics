from bottle import request


def collect_data():
    pass


def routes(config):
    return (
        ('analytics:collect', collect_data,
         'GET', '/analytics/', dict(unlocked=True)),
    )
