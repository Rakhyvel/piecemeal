from django.apps import AppConfig


class PiecemealAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'piecemeal_app'

def ready(self):
    import piecemeal_app.signals