from bottle_utils.i18n import lazy_gettext as _

from librarian_dashboard.dashboard import DashboardPlugin


class AnalyticsDashboardPlugin(DashboardPlugin):
    # Translators, used as dashboard section title
    heading = _('Analytics')
    name = 'analytics'

    def get_template(self):
        return 'dashboard/' + self.name

    def get_context(self):
        return dict()
