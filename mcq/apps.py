from django.apps import AppConfig


class McqConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mcq'

    def ready(self):
        import mcq.signals
