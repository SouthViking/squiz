# Definitions of the functions that will be executed by the global scheduler
from typing import List
from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist

from core.logger import logger
from quizzes.models import Quiz
from scheduler.scheduler import Scheduler
from scheduler.types import AppJobsConfig, DateTimeBasedJobDefinition

def generate_quiz_activation_job_id(quiz_id: int, activation: bool):
    return f'quiz-{quiz_id}-activation-job' if activation else f'quiz-{quiz_id}-deactivation-job'

def generate_quiz_activation_job_definition(quiz: Quiz, activation: bool, custom_run_date: datetime = None) -> DateTimeBasedJobDefinition:
    return {
        'func': quiz_activation_job if activation else quiz_deactivation_job,
        'id': generate_quiz_activation_job_id(quiz.id, activation),
        'args': [quiz.id],
        'run_date': custom_run_date if custom_run_date else ( quiz.starts_at if activation else quiz.deadline ).replace(microsecond = 0),
    }

def quiz_activation_job(quiz_id: int):
    logger.info(f'Executing quiz activation for quiz ID {quiz_id}.')

    try:
        quiz_record = Quiz.objects.get(id = quiz_id)
        
        quiz_record.is_active = True
        quiz_record.draft_mode = False

        quiz_record.save()

        logger.info(f'Quizz with ID {quiz_id} has been activated.')

    except ObjectDoesNotExist:
        logger.error(f'Could not activate quiz with ID {quiz_id}. The quiz does not exist.')

def quiz_deactivation_job(quiz_id: int):
    logger.info(f'Executing quiz deactivation for quiz ID {quiz_id}.')

    try:
        quiz_record = Quiz.objects.get(id = quiz_id)

        quiz_record.is_active = False
        quiz_record.draft_mode = False

        quiz_record.save()

        # TODO: Maybe send an email to the quiz creator to notify that the quiz period has finished.
        # (Thats also the reason why is not DRY-ed with quiz_activation_job)

        logger.info(f'Quizz with ID {quiz_id} has been deactivated.')

    except ObjectDoesNotExist:
        logger.error(f'Could not deactivate quiz with ID {quiz_id}. The quiz does not exist.')

# Adds the jobs to enable/disable quizzes in case the server is restarted. (Since jobs live in memory, they will be removed)
def load_scheduled_quizzes_into_jobs(scheduler: Scheduler):
    try:
        quizzes_to_load = Quiz.objects.filter(use_scheduling = True)
        jobs_to_be_scheduled: List[DateTimeBasedJobDefinition] = []
        logger.debug(f'Found {quizzes_to_load.count()} quizzes to be re-scheduled after server restart.')

        for quiz in quizzes_to_load:
            if quiz.starts_at.replace(tzinfo = None) > datetime.now():
                # TODO: Do not schedule if the gap between the current datetime and starts_at is small
                # Instead, just enable it.
                logger.debug(f'Adding job to schedule the activation of the quiz with ID {quiz.id}.')
                jobs_to_be_scheduled.append(generate_quiz_activation_job_definition(quiz, True))

            else:
                logger.debug(f'Quiz with ID {quiz.id} has already started. Activating it directly.')
                
                quiz.is_active = True
                quiz.save()

            if quiz.deadline.replace(tzinfo = None) > datetime.now():
                logger.debug(f'Adding job to schedule the deactivation of the quiz with ID {quiz.id}.')
                jobs_to_be_scheduled.append(generate_quiz_activation_job_definition(quiz, False))

            else:
                logger.debug(f'Quiz with ID {quiz.id} has already finished. Deactivating it directly.')

                quiz.is_active = False
                quiz.save()

        scheduler.add_datetime_based_jobs(jobs_to_be_scheduled)

    except Exception as error:
        logger.error('There has been an error while trying to execute the load of scheduled quizzes into jobs.')
        logger.error(f'Error: {error}')


initial_jobs_config: AppJobsConfig = {
    'on_start_up_callbacks': [load_scheduled_quizzes_into_jobs]
}