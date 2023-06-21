from django.apps import AppConfig

from notify.constants import NOTIFICATIONS_PER_PAGE


class NotifyConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'notify'

    def ready(self):
        """Overrides notifications per page value"""
        from django.conf import settings
        settings.PAGINATE_BY = NOTIFICATIONS_PER_PAGE
        import notify.signals
