from django.apps import AppConfig


class MsgAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'msg_app'
    verbose_name = 'Telegram Bot Xabarlari'

    def ready(self):
        import msg_app.signals
