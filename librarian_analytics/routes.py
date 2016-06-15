import logging
try:
    from io import BytesIO as StringIO
except ImportError:
    from StringIO import StringIO

from fdsend import send_file
from streamline import RouteBase

from librarian.core.exts import ext_container as exts
from librarian.core.utils import utcnow

from .decorators import install_tracking_cookie
from .helpers import get_payload
from .tasks import store_data


class AnalyticsData(RouteBase):
    name = 'analytics:data'
    path = '/analytics/'
    kwargs = dict(unlocked=True)

    def get(self):
        device_id_file = self.config['analytics.device_id_file']
        db = exts.databases.librarian
        _, payload = get_payload(db, device_id_file, limit=None)
        filename = '{}.stats'.format(utcnow().isoformat())
        return send_file(StringIO(payload), filename, attachment=True)

    @install_tracking_cookie
    def post(self):
        data = dict(path=self.request.params.get('path'),
                    action=self.request.params.get('type'),
                    timezone=float(self.request.params.get('tz')))
        data.update(self.request.tracking_info)
        exts.tasks.schedule(store_data, args=(data,))
        logging.debug("'%s' opener used on '%s'", data['action'], data['path'])
        return 'OK'
