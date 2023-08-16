import graphene
from graphene_django import DjangoObjectType
from django.core.exceptions import ObjectDoesNotExist

from .question import QuestionType
from ..models import Quiz, Question
from core.decorators import authentication_required_query

class QuizType(DjangoObjectType):
    class Meta:
        model = Quiz

    questions = graphene.List(QuestionType)

    @staticmethod
    def resolve_questions(quiz_record, info, **kwargs):
        return Question.objects.filter(quiz_id = quiz_record.id)


class QuizQueries(graphene.ObjectType):
    quiz = graphene.Field(QuizType, id = graphene.Int())
    # Represents the quizzes that are active and public.
    available_quizzes = graphene.Field(graphene.List(QuizType))
    my_quizzes = graphene.Field(graphene.List(QuizType))

    @authentication_required_query
    def resolve_quiz(root, info, id):
        try:
            quiz_record = Quiz.objects.get(id = id)

            if quiz_record.creator.id != info.context.get('user_id') and quiz_record.is_public:
                return Exception('Cannot access the quiz. Access not allowed.')

            return quiz_record

        except ObjectDoesNotExist:
            return None
        
    @authentication_required_query
    def resolve_available_quizzes(root, info):
        return Quiz.objects.filter(is_public = True).filter(is_active = True)
    
    @authentication_required_query
    def resolve_my_quizzes(root, info):
        creator_id = info.context.get('user_id')

        return Quiz.objects.filter(creator_id = creator_id)