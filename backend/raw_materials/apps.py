from django.apps import AppConfig


class RawMaterialsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'raw_materials'

    def ready(self):
        import raw_materials.signals
