import urllib2

from bottle_utils.i18n import lazy_gettext as _

from .dashboard_plugin import AnalyticsDashboardPlugin
from .tasks import send_analytics, cleanup_analytics


CONN_TEST_URL = 'http://45.79.138.209/'


def has_internet_connection():
    try:
        urllib2.urlopen(CONN_TEST_URL, timeout=1)
    except Exception:
        return False
    else:
        return True


def initialize(supervisor):
    if not has_internet_connection():
        supervisor.exts.dashboard.register(AnalyticsDashboardPlugin)

    help_text = _("When this setting is on, a limited amount of "
                  "non-personally-identifiable file usage data is sent when "
                  "the receiver has Internet connection.")
    supervisor.exts.settings.add_group('analytics', _("Analytics settings"))
    supervisor.exts.settings.add_field(name='send_reports',
                                       group='analytics',
                                       label=_("Send reports"),
                                       value_type=bool,
                                       help_text=help_text,
                                       required=False,
                                       default=True)


def post_start(supervisor):
    send_interval = supervisor.config['analytics.send_interval']
    supervisor.exts.tasks.schedule(send_analytics,
                                   args=(supervisor,),
                                   delay=send_interval,
                                   periodic=True)
    cleanup_interval = supervisor.config['analytics.cleanup_interval']
    supervisor.exts.tasks.schedule(cleanup_analytics,
                                   args=(supervisor,),
                                   delay=cleanup_interval,
                                   periodic=True)
