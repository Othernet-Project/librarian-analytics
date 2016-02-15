import urllib2

from bottle_utils.i18n import lazy_gettext as _

from .dashboard_plugin import AnalyticsDashboardPlugin
from .tasks import send_analytics


CONN_TEST_URL = 'http://45.79.138.209/'


def has_internet_connection():
    try:
        urllib2.urlopen(CONN_TEST_URL, timeout=1)
    except urllib2.URLError:
        return False
    else:
        return True


def initialize(supervisor):
    if not has_internet_connection():
        supervisor.exts.dashboard.register(AnalyticsDashboardPlugin)

    supervisor.exts.settings.add_group('analytics', _("Analytics settings"))
    supervisor.exts.settings.add_field(name='send_reports',
                                       group='analytics',
                                       label=_("Send reports"),
                                       value_type=bool,
                                       required=False,
                                       default=True)


def post_start(supervisor):
    send_interval = supervisor.config['analytics.send_interval']
    supervisor.exts.tasks.schedule(send_analytics,
                                   args=(supervisor,),
                                   delay=send_interval,
                                   periodic=True)
