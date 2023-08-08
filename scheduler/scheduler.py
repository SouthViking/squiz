from typing import List, Union
from django.conf import settings
from apscheduler.schedulers.background import BackgroundScheduler

from core.logger import Logger
from core.utils import import_from_module
from .types import IntervalJobDefinition, DateTimeBasedJobDefinition, JobType, AppJobsConfig

class Scheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.logger = Logger('GlobalScheduler', { 'buffer': None })

    def start(self):
        self.load_initial_jobs()

        self.logger.debug('Starting scheduler.')
        self.scheduler.start()
        self.logger.debug('Scheduler has started without issues.')

    def load_initial_jobs(self):
        self.logger.debug(f'Adding initial job configuration for apps: {settings.CUSTOM_APPS}')
        loaded_jobs = {}

        for app_name in settings.CUSTOM_APPS:
            loaded_jobs[app_name] = []       
            try:
                initial_jobs_config: Union[AppJobsConfig, bool] = import_from_module(f'{app_name}.jobs', 'initial_jobs_config')
                if initial_jobs_config is None:
                    self.logger.warn(f'Could not import initial job definitions for app: {app_name}. Likely because they are not defined.')
                    continue

                job_definitions = initial_jobs_config.get('on_start_up_jobs', {})

                for job in job_definitions.get('interval_jobs', []):
                    self.add_job(JobType.INTERVAL, job)
                    loaded_jobs[app_name].append(job['id'])

                for job in job_definitions.get('datetime_jobs', []):
                    self.add_job(JobType.DATETIME, job)
                    loaded_jobs[app_name].append(job['id'])

                app_start_up_callbacks = initial_jobs_config.get('on_start_up_callbacks', [])
                self.logger.debug(f'Found {len(app_start_up_callbacks)} callbacks to execute on startup.')
                
                for start_up_callback in app_start_up_callbacks:
                    self.logger.debug(f'Executing callback: {start_up_callback.__name__} for app {app_name}')
                    start_up_callback(self)

            except Exception as error:
                self.logger.error(f'Got the following error after trying to import jobs configuration from app: {app_name}.')
                self.logger.error(f'Error: {str(error)}')

        self.logger.debug('------ Loaded jobs:')
        self.logger.debug(str(loaded_jobs))


    def add_job(self, type: JobType, job: Union[IntervalJobDefinition, DateTimeBasedJobDefinition]):
        from core.decorators import tryable_function

        if self.scheduler.get_job(job_id = job['id']) is not None:
            self.logger.warn(f'Cannot add job with ID {job["id"]}. A job with this ID has already been registered.')
            return

        if type == JobType.INTERVAL:
            self.logger.debug(f'Adding interval job for job ID: {job["id"]}. Interval seconds = {job["seconds"]}')
            self.scheduler.add_job(
                tryable_function(job['func']),
                'interval',
                id = job.get('id'),
                name = job.get('name', job['func'].__name__),
                args = job.get('args', []),
                kwargs = job.get('kwargs', {}),
                seconds = job['seconds'],
            )
        
        elif type == JobType.DATETIME:
            self.logger.debug(f'Adding datetime based job for job ID: {job["id"]}. Datetime to schedule: {str(job["run_date"])}')
            self.scheduler.add_job(
                tryable_function(job['func']),
                'date',
                id = job.get('id'),
                name = job.get('name', job['func'].__name__),
                args = job.get('args', []),
                kwargs = job.get('kwargs', {}),
                run_date = job['run_date'],
            )

    def add_interval_jobs(self, jobs: List[IntervalJobDefinition]):
        for job_definition in jobs:
            if 'func' not in job_definition or 'seconds' not in job_definition:
                self.logger.warn(f'Function or seconds not defined for interval job definition. Job ID: {job_definition["id"]}')
                continue

            self.add_job(JobType.INTERVAL, job_definition)

    def add_datetime_based_jobs(self, jobs: List[DateTimeBasedJobDefinition]):
        for job_definition in jobs:
            if 'func' not in job_definition or 'run_date' not in job_definition:
                self.logger.warn(f'Function or run date not defined for datetime job definition. Job ID: {job_definition["id"]}')
                continue

            self.add_job(JobType.DATETIME, job_definition)

    def remove_job_by_id(self, job_id: str):
        try:
            if not self.scheduler.get_job(job_id):
                self.logger.error(f'Cannot find a scheduled job with ID: {job_id}. Skipping deletion process.')
                return
            
            self.logger.info(f'Found job with ID {job_id}. Removing it.')
            self.scheduler.remove_job(job_id)

        except Exception as error:
            self.logger.error(f'There has been an error after trying to remove a job by ID: {job_id}')
            self.logger.error(f'Error message: {str(error)}')


scheduler = Scheduler()