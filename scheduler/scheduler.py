from typing import List
from apscheduler.schedulers.background import BackgroundScheduler

from .types import IntervalJobDefinition

class Scheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()

    def start(self):
        from users.jobs import interval_jobs as user_interval_jobs

        self.add_interval_jobs(user_interval_jobs)
        self.scheduler.start()

    def add_interval_jobs(self, jobs: List[IntervalJobDefinition]):
        from core.decorators import tryable_function
        
        for job_definition in jobs:
            if 'seconds' not in job_definition or 'func' not in job_definition:
                continue

            self.scheduler.add_job(
                tryable_function(job_definition['func']),
                'interval',
                name = job_definition.get('name', job_definition['func'].__name__),
                args = job_definition.get('args', []),
                kwargs = job_definition.get('kwargs', {}),
                seconds = job_definition['seconds'],
            )

scheduler = Scheduler()