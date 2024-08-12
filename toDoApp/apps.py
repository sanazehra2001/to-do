from django.apps import AppConfig


class TodoappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'toDoApp'

    def ready(self):
        import toDoApp.signals
        print("TodoappConfig is ready")