from .tasks import send_collected_data


def post_start(supervisor):
    send_interval = supervisor.config['analytics.send_interval']
    supervisor.exts.tasks.schedule(send_collected_data,
                                   args=(supervisor),
                                   delay=send_interval,
                                   periodic=True)
