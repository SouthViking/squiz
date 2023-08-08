import graphene
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist

from .. import logger
from quizzes.models import Question, Option
from core.graphene.common import BaseMutationResult
from core.decorators import tryable_mutation, authentication_required_mutation

class AddOptionToQuestionMutation(graphene.Mutation, BaseMutationResult):
    class Arguments:
        question_id = graphene.Int(required = True)
        label = graphene.String(required = True)
        is_correct = graphene.Boolean()
        feedback_message = graphene.String()

    option_id = graphene.Int()

    @authentication_required_mutation
    @tryable_mutation()
    def mutate(root, info, **data):
        try:
            question_record = Question.objects.get(id = data['question_id'])
            if question_record.quiz.creator.id != info.context['user_id']:
                return {
                    'success': False,
                    'message': 'Cannot add the option to the question. Operation not allowed',
                    'status_code': 403,
                }

            if question_record.quiz.is_active:
                return {
                    'success': False,
                    'message': 'Cannot add the option to the question. The quiz is currently active.',
                    'status_code': 409,
                }
            
            if data.get('is_correct', False):
                pass
                # TODO: In case the quiz already has user's answers, the total points of those that answered the quiz need to be calculated again
                # in case the new option that is being added is marked as the correct one.
            
            current_correct_option = Option.objects.filter(question_id = question_record.id).filter(is_correct = True)
            if len(current_correct_option) != 0 and data.get('is_correct', False):
                return {
                    'success': False,
                    'message': 'There can only be 1 correct option per question.',
                    'status_code': 409,
                }
            
            logger.info(f'Executing mutation to add option to question ID {question_record.id}.')

            new_option = Option(
                    label = data['label'],
                    is_correct = data.get('is_correct', False),
                    feedback_message = data.get('feedback_message', ''),
                    question = question_record,
                )
            new_option.save()

            logger.info(f'New option (ID: {new_option.id}) has been added to the question options. Question ID: {question_record.id}.')

            return {
                'success': True,
                'message': 'The option has been added to the question.',
                'option_id': new_option.id,
                'status_code': 201,
            }
        except ObjectDoesNotExist:
            return {
                'success': False,
                'message': 'The question is not available.',
                'status_code': 404,
            }
        
class SetCorrectOptionMutation(graphene.Mutation, BaseMutationResult):
    class Arguments:
        option_id = graphene.Int(required = True)

    @authentication_required_mutation
    @tryable_mutation()
    def mutate(root, info, **data):
        try:
            option_record = Option.objects.get(id = data['option_id'])
            if option_record.question.quiz.creator.id != info.context['user_id']:
                return {
                    'success': False,
                    'message': 'Cannot update the option. Operation not allowed',
                    'status_code': 403,
                }
            
            if option_record.question.quiz.is_active:
                return {
                    'success': False,
                    'message': 'Cannot update the options while the quiz is active.',
                    'status_code': 409,
                }

            correct_option_filter = Option.objects.filter(question_id = option_record.question.id).filter(is_correct = True)\

            with transaction.atomic():
                if len(correct_option_filter) != 0:
                    current_correct_option = correct_option_filter[0]

                    logger.debug(f'Current correct option for question (ID: {option_record.question.id}) is option ID {current_correct_option.id}. Setting it as False.')

                    current_correct_option.is_correct = False
                    current_correct_option.save()

                option_record.is_correct = True
                option_record.save()
                
                logger.info(f'Option with ID {option_record.id} has been marked as the correct one for question ID {option_record.question.id}.')

            # TODO: In case the quiz already has user's answers, the total points of those that answered the quiz need to be calculated again
            # regarding the new correct option (if it really changed)

            return {
                'success': True,
                'message': 'The option has been marked as the correct one.',
                'status_code': 200,
            }

        except ObjectDoesNotExist:
            return {
                'success': False,
                'message': 'The option is not available.',
                'status_code': 404,
            }