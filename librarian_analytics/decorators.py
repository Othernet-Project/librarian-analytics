import functools

from bottle import request, response
from bottle_utils.lazy import caching_lazy

from . import data


EXPORTS = {
    'tracking_id_cookie_plugin': {},
}


@caching_lazy
def prepare_device_id(path):
    try:
        with open(path, 'w') as f:
            current_key = f.read()
    except IOError:
        current_key = ''
    if not current_key:
        # No key has been set yet
        current_key = data.generate_device_id()
        with open(path, 'w') as f:
            f.write(current_key)
    assert current_key != '', "'My dog ate it' is a poor excuse"
    return current_key


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
        tracking_cookie_name = config['analytics.tracking_cookie_name']
        device_id_file = config['analytics.device_id_file']
        device_id = prepare_device_id(device_id_file)
        request.device_id = device_id
        set_track_id(tracking_cookie_name)
        return fn(*args, **kwargs)
    return wrapper
