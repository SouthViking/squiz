from graphene_django import DjangoObjectType

from ..models import Option

class OptionType(DjangoObjectType):
    class Meta:
        model = Option