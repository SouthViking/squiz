import graphene

from users.models import User
from quizzes.models import Quiz
from quizzes.utils import is_quiz_time_interval_valid
from core.decorators import tryable_mutation, authentication_required_mutation

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

class QuizCreationMutation(graphene.Mutation):
    class Arguments:
        title = graphene.String(required = True)
        summary = graphene.String()
        max_solving_time_mins = graphene.Int(required = True)
        is_public = graphene.Boolean()
        is_scheduled = graphene.Boolean()
        starts_at = graphene.DateTime()
        deadline = graphene.DateTime()

    class Meta:
        description = 'Creates a new base quiz.'

    success = graphene.Boolean()
    message = graphene.String()
    quiz = graphene.Field(QuizObject)
    internal_message = graphene.String()

    @authentication_required_mutation
    @tryable_mutation(required_fields = ['title', 'max_solving_time_mins', 'starts_at', 'deadline'])
    def mutate(root, info, **data):
        user_id: int = info.context['user_id']

        are_valid_datetimes, error = is_quiz_time_interval_valid(data['starts_at'], data['deadline'], data['max_solving_time_mins'])
        if not are_valid_datetimes:
            return {
                'success': False,
                'message': f'The quiz date and times are not valid: {error}',
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
        
        # TODO: Scheduling process for quizzes that have 'is_scheduled' = True.

        return {
            'success': True,
            'message': f'The quiz \"{new_quiz.title}\" has been created correctly.',
            'quiz': new_quiz,
        }
