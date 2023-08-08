import humps
import graphene
from datetime import datetime
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist

from users.models import User
from core.utils import camelize_list
from scheduler.scheduler import scheduler
from quizzes.models import Quiz, Question, Option, UserQuiz
from core.graphene.common import BaseMutationResult, FieldUpdateErrorInfo
from core.decorators import tryable_mutation, authentication_required_mutation
from quizzes.utils import is_quiz_time_interval_valid, is_solving_time_in_between_datetimes
from quizzes.jobs import generate_quiz_activation_job_definition, generate_quiz_activation_job_id

class QuizObject(graphene.ObjectType):
    title = graphene.String()
    summary = graphene.String()
    max_solving_time_mins = graphene.Int()
    is_active = graphene.Boolean()
    is_public = graphene.Boolean()
    use_scheduling = graphene.Boolean()
    starts_at = graphene.DateTime()
    deadline = graphene.DateTime()
    created_at = graphene.DateTime()

class QuizCreationMutation(graphene.Mutation, BaseMutationResult):
    class Arguments:
        title = graphene.String(required = True)
        summary = graphene.String()
        max_solving_time_mins = graphene.Int(required = True)
        is_public = graphene.Boolean()
        use_scheduling = graphene.Boolean()
        starts_at = graphene.DateTime()
        deadline = graphene.DateTime()
        draft_mode = graphene.Boolean()

    class Meta:
        description = 'Creates a new base quiz.'

    quiz = graphene.Field(QuizObject)

    @authentication_required_mutation
    @tryable_mutation(required_fields = ['title', 'max_solving_time_mins', 'starts_at', 'deadline'])
    def mutate(root, info, **data):
        user_id: int = info.context['user_id']

        are_valid_datetimes, error = is_quiz_time_interval_valid(data['starts_at'], data['deadline'], data['max_solving_time_mins'])
        if not are_valid_datetimes:
            return {
                'success': False,
                'message': f'The quiz date and times are not valid: {error}',
                'status_code': 400,
            }

        new_quiz = Quiz(
            title = data['title'],
            summary = data.get('summary', None),
            max_solving_time_mins = data['max_solving_time_mins'],
            is_public = data.get('is_public', False),
            use_scheduling = data.get('use_scheduling', False),
            starts_at = data['starts_at'],
            deadline = data['deadline'],
            creator = User.objects.get(id = user_id),
            draft_mode = data.get('draft_mode', True),
        )
        new_quiz.save()
        
        if data.get('use_scheduling', False) and not data.get('draft_mode', True):
            # If the quiz is in 'draft mode', then it means that in the client side can still be edited
            # so shouldn't be prepared to be published until the flag is manually changed.
            scheduler.add_datetime_based_jobs([
                generate_quiz_activation_job_definition(new_quiz, True),
                generate_quiz_activation_job_definition(new_quiz, False)
            ])

        return {
            'success': True,
            'message': f'The quiz \"{new_quiz.title}\" has been created correctly.',
            'quiz': new_quiz,
            'status_code': 201,
        }

class QuizUpdateMutation(graphene.Mutation, BaseMutationResult):
    class Arguments:
        id = graphene.Int(required = True)
        title = graphene.String()
        summary = graphene.String()
        max_solving_time_mins = graphene.Int()
        is_public = graphene.Boolean()

    class Meta:
        description = 'Allows to update specific quiz fields.'

    quiz = graphene.Field(QuizObject)
    updated_fields = graphene.List(graphene.String)
    fields_with_error = graphene.List(FieldUpdateErrorInfo)
    
    @authentication_required_mutation
    @tryable_mutation(required_fields = ['id'])
    def mutate(root, info, **data):
        try:
            quiz_record = Quiz.objects.get(id = data['id'])
            updated_fields = []
            fields_with_error = []

            if quiz_record.creator.id != info.context['user_id']:
                return {
                    'success': False,
                    'message': 'Cannot update the quiz. Operation not allowed.',
                    'status_code': 403,
                }
            
            for field in data:
                if field == 'id':
                    continue

                if type(data[field]) == str and len(data[field].strip()) == 0:
                    fields_with_error.append({
                        'field': humps.camelize(field),
                        'error': 'The field cannot be empty.',
                    })
                    continue

                if field == 'max_solving_time_mins':
                    if not is_solving_time_in_between_datetimes(quiz_record.starts_at, quiz_record.deadline, data['max_solving_time_mins']):
                        fields_with_error.append({
                            'field': humps.camelize(field),
                            'error': 'The time interval defined is not valid regarding the current start and end time for the quiz.'
                        })
                        continue

                setattr(quiz_record, field, data[field])
                updated_fields.append(field)

            quiz_record.save()
            camelize_list(updated_fields)

            return {
                'success': True,
                'message': 'The quiz has been updated.',
                'updated_fields': updated_fields,
                'fields_with_error': fields_with_error,
                'quiz': quiz_record,
                'status_code': 200,
            }

        except ObjectDoesNotExist:
            return {
                'success': False,
                'message': 'The target quiz does not exist.',
                'status_code': 404,
            }
        
class QuizReScheduleMutation(graphene.Mutation, BaseMutationResult):
    class Arguments:
        quiz_id = graphene.Int(required = True)
        starts_at = graphene.DateTime()
        deadline = graphene.DateTime()
        use_scheduling = graphene.Boolean()

    description = 'Allows to reschedule a quiz by modifying either its start or end time, or enabling/disabling the scheduling option.'

    @authentication_required_mutation
    @tryable_mutation()
    def mutate(root, info, **data):
        try:
            quiz_record = Quiz.objects.get(id = data['quiz_id'])
            if quiz_record.is_active:
                return {
                    'success': False,
                    'message': 'Cannot reschedule the quiz. It is currently active.',
                    'status_code': 409,
                }

            new_starts_at = data['starts_at'] if 'starts_at' in data else quiz_record.starts_at
            new_deadline = data['deadline'] if 'deadline' in data else quiz_record.deadline
            new_use_scheduling = data['use_scheduling'] if 'use_scheduling' in data else quiz_record.use_scheduling

            valid, error = is_quiz_time_interval_valid(new_starts_at, new_deadline, quiz_record.max_solving_time_mins)
            if not valid:
                return {
                    'success': False,
                    'message': error,
                    'status_code': 409,
                }
            
            quiz_record.starts_at = new_starts_at
            quiz_record.deadline = new_deadline
            quiz_record.use_scheduling = new_use_scheduling
            quiz_record.save()

            # Remove the current jobs in case they were scheduled.
            scheduler.remove_job_by_id(generate_quiz_activation_job_id(quiz_record.id, True))
            scheduler.remove_job_by_id(generate_quiz_activation_job_id(quiz_record.id, False))

            if new_use_scheduling:
                # Schedule the new jobs regarding the updated values for starts_at and deadline
                scheduler.add_datetime_based_jobs([
                    generate_quiz_activation_job_definition(quiz_record, True),
                    generate_quiz_activation_job_definition(quiz_record, False)
                ])

            return {
                'success': True,
                'message': 'The quiz has been rescheduled correctly.',
                'status_code': 200,
            }

        except ObjectDoesNotExist:
            return {
                'success': False,
                'message': 'The target quiz does not exist.',
                'status_code': 404,
            }

class UserStartQuizMutation(graphene.Mutation, BaseMutationResult):
    class Arguments:
        quiz_id = graphene.Int(required = True)

    class Meta:
        description = 'Generates a new record to mark the quiz as started by the user.'

    @authentication_required_mutation
    @tryable_mutation()
    def mutate(root, info, **data):
        try:
            user_record: User = User.objects.get(id = info.context['user_id'])
            quiz_record = Quiz.objects.get(id = data['quiz_id'])

            user_quiz_register = user_record.solved_quizzes.filter(id= data['quiz_id'])
            
            if user_quiz_register.count() != 0:
                return {
                    'success': False,
                    'message': 'Cannot start the quiz. It has been already started by the user.',
                    'status_code': 409,
                }

            if not quiz_record.is_public and quiz_record.creator.id != user_record.id:
                return {
                    'success': False,
                    'message': 'Cannot start this quiz. It is not public.',
                    'status_code': 409,
                }
            
            if not quiz_record.is_active:
                return {
                    'success': False,
                    'message': 'Cannot start the quiz. It is currently inactive.',
                    'status_code': 409,
                }
            
            user_record.solved_quizzes.add(quiz_record, through_defaults = {
                'total_score': 0,
            })


            return { 'success': True, 'status_code': 200 }

        except ObjectDoesNotExist:
            return {
                'success': False,
                'message': 'The target quiz/user does not exist',
                'status_code': 404,
            }
        
class SubmitQuizAnswersMutation(graphene.Mutation, BaseMutationResult):
    class Arguments:
        quiz_id = graphene.Int()
        # An array containing the IDs of the selected options. (Internally we know the questions that they are attached to)
        selected_options = graphene.List(graphene.Int)

    class Meta:
        description = 'Registers the answers and marks the quiz as finished for the user.'

    not_answered_questions = graphene.List(graphene.Int)

    @authentication_required_mutation
    @tryable_mutation()
    def mutate(root, info, **data):
        try:
            user_record: User = User.objects.get(id = info.context['user_id'])
            quiz_record = Quiz.objects.get(id = data['quiz_id'])

            user_quiz_register = user_record.solved_quizzes.through.objects.all()
            if user_quiz_register.count() == 0:
                return {
                    'success': False,
                    'message': 'Cannot register the answers. You need to start it first.',
                    'status_code': 409,
                }
            user_quiz_register: UserQuiz = user_quiz_register[0]
            
            
            if not quiz_record.is_public and quiz_record.creator.id != user_record.id:
                return {
                    'success': False,
                    'message': 'Cannot register the answers. It is not public.',
                    'status_code': 409,
                }
            
            if not quiz_record.is_active:
                return {
                    'success': False,
                    'message': 'Cannot register the answers. It is currently inactive.',
                    'status_code': 409,
                }
            
            if user_quiz_register.finished_at is not None:
                return {
                    'success': False,
                    'message': 'Cannot register the answers. The quiz has already been marked as submitted.',
                }
            
            real_score = 0

            expected_questions = Question.objects.values_list('id').get(quiz_id = quiz_record.id)
            expected_questions_map = {}
            for expected_question_id in expected_questions:
                expected_questions_map[expected_question_id] = True


            with transaction.atomic():
                options_to_add = []
                for selected_option_id in data.get('selected_options', []):
                    try:
                        option_record = Option.objects.get(id = selected_option_id)
                    except ObjectDoesNotExist:
                        return {
                            'success': False,
                            'message': f'Option with ID: {selected_option_id} is not valid. It does not reference any question.',
                        }
                    
                    if option_record.question.id not in expected_questions_map:
                        # The selected option is not attached to a valid question of the current quiz.
                        # Just skip.
                        continue

                    del expected_questions_map[option_record.question.id]

                    real_score += option_record.is_correct * option_record.question.score

                    options_to_add.append(option_record)

                if len(expected_questions_map) != 0:
                    return {
                        'success': False,
                        'message': 'Some questions were not answered.',
                        'not_answered_questions': expected_questions_map.keys()
                    }

                for option in options_to_add:
                    user_record.selections.add(option)

                user_quiz_register.finished_at = datetime.now()
                user_quiz_register.total_score = real_score
                user_quiz_register.save()
            
            return {
                'success': True,
                'message': 'The quiz has been submited correctly.',
            }

        except ObjectDoesNotExist:
            return {
                'success': False,
                'message': 'The target quiz/user does not exist',
                'status_code': 404,
            }