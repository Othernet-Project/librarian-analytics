import urllib2


CONN_TEST_URL = 'http://45.79.138.209/'


def has_internet_connection():
    try:
        urllib2.urlopen(CONN_TEST_URL, timeout=1)
    except Exception:
        return False
    else:
        return True
