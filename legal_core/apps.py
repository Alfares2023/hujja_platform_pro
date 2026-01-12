from django.apps import AppConfig

class LegalCoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'legal_core'

    def ready(self):
        import legal_core.signals # استيراد التنبيهات عند الجاهزية