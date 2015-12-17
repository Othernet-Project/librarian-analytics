import uuid

import user_agents


FIELD_SEPARATOR = '$'
DESKTOP = 1
PHONE = 2
TABLET = 3
OTHER = 0


def generate_device_id():
    return str(uuid.uuid4())


def generate_user_id():
    return uuid.uuid4().hex[:8]


def characterize_agent(ua_string):
    ua = user_agents.parse(ua_string)
    os_fam = ua.os.family
    if ua.is_pc:
        return (os_fam, DESKTOP)
    elif ua.is_tablet:
        return (os_fam, TABLET)
    elif ua.is_mobile:
        return (os_fam, PHONE)
    return (os_fam, OTHER)


def serialize_cookie_data(*args):
    return FIELD_SEPARATOR.join(str(a) for a in args)


def deserialize_cookie_data(data):
    try:
        user_id, os_fam, agent_type = data.split(FIELD_SEPARATOR)
        agent_type = int(agent_type)
        assert agent_type in [DESKTOP, TABLET, PHONE, OTHER], 'Invalid type?'
        assert len(user_id) == 8, 'Invalid user ID?'
        return user_id, os_fam, agent_type
    except (ValueError, TypeError):
        return None
