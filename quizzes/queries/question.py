import graphene
from graphene_django import DjangoObjectType

from .option import OptionType
from ..models import Question, Option

class QuestionType(DjangoObjectType):
    class Meta:
        model = Question

    options = graphene.List(OptionType)

    @staticmethod
    def resolve_options(question_record, info, **kwargs):
        return Option.objects.filter(question_id = question_record.id)