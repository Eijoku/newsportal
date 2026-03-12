from django.apps import AppConfig


class NewsportalConfig(AppConfig):
    name = 'NewsPortal'

    def ready(self):
        import NewsPortal.signals