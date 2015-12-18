from .tasks import SendAnalyticsTask


def post_start(supervisor):
    send_interval = supervisor.config['analytics.send_interval']
    supervisor.exts.tasks.schedule(SendAnalyticsTask,
                                   args=(supervisor,),
                                   delay=send_interval,
                                   periodic=True)
