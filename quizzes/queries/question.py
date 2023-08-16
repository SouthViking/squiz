import graphene
from graphene_django import DjangoObjectType
from django.core.exceptions import ObjectDoesNotExist

from .option import OptionType
from ..models import Question, Option
from core.decorators import authentication_required_query

class QuestionType(DjangoObjectType):
    class Meta:
        model = Question

    options = graphene.List(OptionType)

    @staticmethod
    def resolve_options(question_record, info, **kwargs):
        return Option.objects.filter(question_id = question_record.id)
    

class QuestionQueries(graphene.ObjectType):
    question = graphene.Field(QuestionType, id = graphene.Int())

    @authentication_required_query
    def resolve_question(root, info, id):
        try:
            question_record = Question.objects.get(id = id)

            if question_record.quiz.creator.id != info.context.get('user_id'):
                # TODO: Allow to get the question in case the user started solving the quiz.
                raise Exception('Cannot get the question. Access not allowed.')
            
            return question_record

        except ObjectDoesNotExist:
            return None