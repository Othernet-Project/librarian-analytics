from bottle_utils.i18n import lazy_gettext as _


class AnalyticsSetting:
    group = 'analytics'
    verbose_group = _("Analytics settings")
    name = 'send_reports'
    label = _("Send reports")
    value_type = bool
    help_text = _("When this setting is on, a limited amount of "
                  "non-personally-identifiable file usage data is sent when "
                  "the receiver has Internet connection.")
    required = False
    default = True

    @property
    def rules(self):
        return dict(name=self.name,
                    group=self.group,
                    label=self.label,
                    value_type=self.value_type,
                    help_text=self.help_text,
                    required=self.required,
                    default=self.default)
