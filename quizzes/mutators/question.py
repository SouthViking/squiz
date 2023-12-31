import humps
import graphene
from typing import List
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist

from .. import logger
from core.utils import camelize_list
from quizzes.models import Question, Quiz, Option
from core.graphene.common import BaseMutationResult, FieldUpdateErrorInfo
from core.decorators import tryable_mutation, authentication_required_mutation

class OptionObject(graphene.InputObjectType):
    label = graphene.String(required = True)
    is_correct = graphene.Boolean()
    feedback_message = graphene.String()

class QuestionCreationMutation(graphene.Mutation, BaseMutationResult):
    class Arguments:
        quiz_id = graphene.Int(required = True)
        title = graphene.String(required = True)
        description = graphene.String()
        score = graphene.Int()
        options = graphene.List(OptionObject)

    @authentication_required_mutation
    @tryable_mutation(required_fields = ['quiz_id', 'title'])
    def mutate(root, info, **data):
        try:
            user_id: int = info.context['user_id']
            quiz_record = Quiz.objects.get(id = data['quiz_id'])
            
            if quiz_record.creator.id != user_id:
                return {
                    'success': False,
                    'message': 'Cannot add the question to the quiz. The operation is not allowed.',
                    'status_code': 403,
                }
            
            if quiz_record.is_active:
                return {
                    'success': False,
                    'message': 'Cannot add the question to the quiz. The quiz is currently active.',
                    'status_code': 409,
                }
            try:

                logger.info(f'Executing mutation to create question in quiz with ID {quiz_record.id}.')

                with transaction.atomic():
                    logger.debug('Starting transaction to register question and answers.')

                    question = Question(
                        title = data['title'],
                        description = data.get('description', ''),
                        score = data.get('score', 0),
                        quiz = quiz_record
                    )
                    question.save()

                    logger.debug(f'Question has been stored correctly (ID: {question.id}).')

                    options_to_create: List[Option] = []
                    for option in data.get('options', []):
                        options_to_create.append(
                            Option(
                                label = option['label'],
                                is_correct = option.get('is_correct', False),
                                feedback_message = option.get('feedback_message', ''),
                                question = question,
                            )
                        )

                    logger.debug(f'Options to create in question with ID {question.id}: {options_to_create}.')
                    
                    Option.objects.bulk_create(options_to_create)
                    logger.debug(f'Options have been inserted correctly for question with ID {question.id}.')

            except Exception as error:
                return {
                    'success': False,
                    'message': 'There has been an internal error while trying to create the question/options.',
                    'internalMessage': str(error),
                    'status_code': 500,
                }


        except ObjectDoesNotExist:
            return {
                'success': False,
                'message': f'Quiz with ID {data["quiz_id"]} not found.',
                'status_code': 404,
            }

        return {
            'success': True,
            'message': 'The question has been added to the quiz.',
            'status_code': 201,
        }
    
class QuestionUpdateMutation(graphene.Mutation, BaseMutationResult):
    class Arguments:
        id = graphene.Int(required = True)
        title = graphene.String()
        description = graphene.String()
        score = graphene.Int()

    updated_fields = graphene.List(graphene.String)
    fields_with_error = graphene.List(FieldUpdateErrorInfo)

    @authentication_required_mutation
    @tryable_mutation()
    def mutate(root, info, **data):
        try:
            question_record = Question.objects.get(id = data['id'])
            if question_record.quiz.creator.id != info.context['user_id']:
                return {
                    'success': False,
                    'message': 'The question cannot be modified. Operation not allowed.',
                    'status_code': 403,
                }
            
            updated_fields = []
            fields_with_error = []
            allowed_empty_fields = ['description']

            logger.info(f'Executing update mutation for question with ID {question_record.id}.')
            
            for field in data:
                if type(data[field]) == str and len(data[field].strip()) == 0 and field not in allowed_empty_fields:
                    logger.warn(f'Got an empty value for required string field {field} during update mutation for question {question_record.id}.')
                    fields_with_error.append({
                        'field': humps.camelize(field),
                        'error': 'The field cannot be empty.',
                    })
                    continue

                if field == 'score' and data[field] < 0:
                    fields_with_error.append({
                        'field': humps.camelize(field),
                        'error': 'The score field cannot be a negative number.'
                    })
                    continue

                setattr(question_record, field, data[field])
                updated_fields.append(field)

            question_record.save()

            logger.debug(f'Question with ID {question_record.id} has been updated. Updated fields: {updated_fields} | Fields with error: {fields_with_error}')

            camelize_list(updated_fields)

            return {
                'success': True,
                'message': 'The question has been updated.',
                'updated_fields': updated_fields,
                'fields_with_error': fields_with_error,
                'status_code': 200,
            }


        except ObjectDoesNotExist:
            return {
                'success': False,
                'message': 'The target question does not exist.',
                'status_code': 404,
            }
        
class QuestionDeleteMutation(graphene.Mutation, BaseMutationResult):
    class Arguments:
        question_id = graphene.Int()
    
    class Meta:
        description = 'Deletes a question with its options from a quiz.'
    
    @authentication_required_mutation
    @tryable_mutation()
    def mutate(root, info, **data):
        try:
            question_record = Question.objects.get(id = data['question_id'])
            if question_record.quiz.creator.id != info.context['user_id']:
                return {
                    'success': False,
                    'message': 'The question cannot be deleted. Operation not allowed.',
                    'status_code': 403,
                }
            
            if question_record.quiz.is_active:
                return {
                    'success': False,
                    'message': 'Cannot delete the question. The quiz is currently active.',
                    'status_code': 409,
                }
            
            # TODO: If there are user answers, then remove those from the table as well.

            logger.info(f'Executing mutation to remove question with ID {question_record.id}.')

            # Since there is a foreign key to the question in the option table, then the deletion will cascade.
            question_record.delete()

            logger.info(f'Question with ID {question_record.id} has been removed correctly.')


        except ObjectDoesNotExist:
            return {
                'success': False,
                'message': 'The target question does not exist',
                'status_code': 404,
            }

        return {
            'success': True,
            'message': f'The question has been removed from the quiz "{question_record.quiz.title}"',
            'status_code': 200,
        }
