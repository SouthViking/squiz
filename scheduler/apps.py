from django.apps import AppConfig

from .scheduler import scheduler

class SchedulerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'scheduler'

    def ready(self) -> None:
        scheduler.start()
        return super().ready()
