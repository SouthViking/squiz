import graphene
from graphene_django import DjangoObjectType
from django.core.exceptions import ObjectDoesNotExist

from ..models import Option
from core.decorators import authentication_required_query

class OptionType(DjangoObjectType):
    class Meta:
        model = Option

class OptionQueries(graphene.ObjectType):
    option = graphene.Field(OptionType, id = graphene.Int())

    @authentication_required_query
    def resolve_option(root, info, id):
        try:
            option_record = Option.objects.get(id = id)

            if option_record.question.quiz.creator.id != info.context.get('user_id'):
                # TODO: Allow to get the option in case the user started solving the quiz.
                raise Exception('Cannot get the option. Access not allowed.')
            
            return option_record

        except ObjectDoesNotExist:
            return None