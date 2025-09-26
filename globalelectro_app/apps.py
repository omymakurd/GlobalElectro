from django.apps import AppConfig



class GlobalelectroAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'globalelectro_app'
    def ready(self):
        import globalelectro_app.signals