from .dashboard_plugin import AnalyticsDashboardPlugin
from .tasks import send_analytics


def initialize(supervisor):
    supervisor.exts.dashboard.register(AnalyticsDashboardPlugin)


def post_start(supervisor):
    send_interval = supervisor.config['analytics.send_interval']
    supervisor.exts.tasks.schedule(send_analytics,
                                   args=(supervisor,),
                                   delay=send_interval,
                                   periodic=True)
