import functools

from bottle import request, response

from . import data
from .helpers import prepare_device_id


def set_track_id(cookie_name):
    cookie_data = request.get_cookie(cookie_name)
    if cookie_data:
        # Cookie is already set, so we don't touch it
        user_id, os_fam, agent_type = data.deserialize_cookie_data(cookie_data)
        request.tracking_info = {
            'user_id': user_id,
            'os_family': os_fam,
            'agent_type': agent_type,
        }
        return

    # Generate new cookie data
    user_id = data.generate_user_id()
    ua = request.headers.get('User-Agent')
    os_fam, agent_type = data.characterize_agent(ua)
    request.tracking_info = {
        'user_id': user_id,
        'os_family': os_fam,
        'agent_type': agent_type,
    }
    cookie_data = data.serialize_cookie_data(user_id, os_fam, agent_type)
    response.set_cookie(cookie_name, cookie_data, path='/')


def install_tracking_cookie(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        config = request.app.supervisor.config
        # report sending might be disabled in config
        if config.get('analytics.send_reports', False):
            return 'OK'
        tracking_cookie_name = config['analytics.tracking_cookie_name']
        device_id_file = config['analytics.device_id_file']
        device_id = prepare_device_id(device_id_file)
        request.device_id = device_id
        set_track_id(tracking_cookie_name)
        return fn(*args, **kwargs)
    return wrapper
