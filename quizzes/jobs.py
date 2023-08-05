# Definitions of the functions that will be executed by the global scheduler
from django.core.exceptions import ObjectDoesNotExist

from core.logger import logger
from quizzes.models import Quiz

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

        