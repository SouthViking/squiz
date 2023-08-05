import humps
import graphene
from django.core.exceptions import ObjectDoesNotExist

from users.models import User
from quizzes.models import Quiz
from core.utils import camelize_list
from scheduler.scheduler import scheduler
from quizzes.jobs import quiz_activation_job, quiz_deactivation_job
from core.graphene.common import BaseMutationResult, FieldUpdateErrorInfo
from core.decorators import tryable_mutation, authentication_required_mutation
from quizzes.utils import is_quiz_time_interval_valid, is_solving_time_in_between_datetimes

class QuizObject(graphene.ObjectType):
    title = graphene.String()
    summary = graphene.String()
    max_solving_time_mins = graphene.Int()
    is_active = graphene.Boolean()
    is_public = graphene.Boolean()
    is_scheduled = graphene.Boolean()
    starts_at = graphene.DateTime()
    deadline = graphene.DateTime()
    created_at = graphene.DateTime()

class QuizCreationMutation(graphene.Mutation, BaseMutationResult):
    class Arguments:
        title = graphene.String(required = True)
        summary = graphene.String()
        max_solving_time_mins = graphene.Int(required = True)
        is_public = graphene.Boolean()
        is_scheduled = graphene.Boolean()
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
            is_scheduled = data.get('is_scheduled', False),
            starts_at = data['starts_at'],
            deadline = data['deadline'],
            creator = User.objects.get(id = user_id),
        )
        new_quiz.save()
        
        if data.get('is_scheduled', False) and not data.get('draft_mode', True):
            # If the quiz is in 'draft mode', then it means that in the client side can still be edited
            # so shouldn't be prepared to be published until the flag is manually changed.
            scheduler.add_datetime_based_jobs([{
                'func': quiz_activation_job,
                'id': f'quiz-{new_quiz.id}-activation-job',
                'args': [new_quiz.id],
                'run_date': new_quiz.starts_at.replace(microsecond = 0)
            }, {
                'func': quiz_deactivation_job,
                'id': f'quiz-{new_quiz.id}-deactivation-job',
                'args': [new_quiz.id],
                'run_date': new_quiz.deadline.replace(microsecond = 0)
            }])

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

            # TODO: Handle schedule process in case `is_scheduled` is updated to False (need to stop the task if exists)
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