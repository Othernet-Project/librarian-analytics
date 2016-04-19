import calendar
import datetime
import functools
import hashlib
import logging
import uuid

import user_agents

from bitpack import BitStream, BitField, register_data_type
from bitpack.utils import pack, unpack
from bottle_utils.common import to_bytes
from pytz import utc


FIELD_SEPARATOR = '$'

DESKTOP = 1
PHONE = 2
TABLET = 3
OTHER = 0
AGENT_TYPES = [DESKTOP, PHONE, TABLET, OTHER]
ACTIONS = ['file', 'html', 'image', 'audio', 'video', 'folder', 'download']

# !!! DO NOT CHANGE THE ORDER OF ELEMENTS IN THE OS_FAMILIES LIST !!!

OS_FAMILIES = [
    'Android',
    'Arch Linux',
    'BackTrack',
    'Bada',
    'BlackBerry OS',
    'BlackBerry Tablet OS',
    'CentOS',
    'Chrome OS',
    'Debian',
    'Fedora',
    'Firefox OS',
    'FreeBSD',
    'Gentoo',
    'Intel Mac OS',
    'iOS',
    'Kindle',
    'Linux',
    'Linux Mint',
    'Lupuntu',
    'Mac OS',
    'Mac OS X',
    'Mageia',
    'Mandriva',
    'NetBSD',
    'OpenBSD',
    'openSUSE',
    'PCLinuxOS',
    'PPC Mac OS',
    'Puppy',
    'Red Hat',
    'Slackware',
    'Solaris',
    'SUSE',
    'Symbian OS',
    'Ubuntu',
    'Windows 10',
    'Windows 2000',
    'Windows 7',
    'Windows 8',
    'Windows 8.1',
    'Windows 95',
    'Windows 98',
    'Windows CE',
    'Windows ME',
    'Windows Mobile',
    'Windows Phone',
    'Windows RT',
    'Windows RT 8.1',
    'Windows Vista',
    'Windows XP',
]


def from_utc_timestamp(timestamp):
    """Converts the passed-in unix UTC timestamp into a datetime object."""
    timestamp = float(unpack('>i', timestamp))
    dt = datetime.datetime.utcfromtimestamp(timestamp)
    return dt.replace(tzinfo=utc)


def to_utc_timestamp(dt):
    """Converts the passed-in datetime object into a unix UTC timestamp."""
    if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
        msg = "Naive datetime object passed. It is assumed that it's in UTC."
        logging.warning(msg)
    elif dt.tzinfo != utc:
        # local datetime with tzinfo
        return pack('>i', calendar.timegm(dt.utctimetuple()))
    return pack('>i', calendar.timegm(dt.timetuple()))


register_data_type('timestamp', to_utc_timestamp, from_utc_timestamp)


def generate_device_id():
    return uuid.uuid4().hex


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


def round_to_nearest(n):
    return round(n * 2) / 2


def get_timezone_table(start=-12, end=14, step=0.5):
    tz_range = range(start, end)
    return functools.reduce(lambda x, i: x + [i, i + step], tz_range, [])


class StatBitStream(BitStream):
    start_marker = 'OHD'
    end_marker = 'DHO'
    user_id = BitField(width=32, data_type='hex')
    timestamp = BitField(width=32, data_type='timestamp')
    timezone = BitField(width=6, data_type='integer')
    path = BitField(width=128, data_type='hex')
    action = BitField(width=4, data_type='integer')
    os_family = BitField(width=6, data_type='integer')
    agent_type = BitField(width=2, data_type='integer')

    def preprocess_path(self, value):
        return hashlib.md5(to_bytes(value)).hexdigest()

    def preprocess_timezone(self, value):
        rounded_tz = round_to_nearest(value)
        return get_timezone_table().index(rounded_tz)

    def postprocess_timezone(self, value):
        return get_timezone_table()[value]

    def preprocess_action(self, value):
        return ACTIONS.index(value)

    def postprocess_action(self, value):
        return ACTIONS[value]

    def preprocess_os_family(self, value):
        return OS_FAMILIES.index(value)

    def postprocess_os_family(self, value):
        return OS_FAMILIES[value]
