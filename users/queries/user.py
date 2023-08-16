import humps
import graphene
from graphene_django import DjangoObjectType
from django.core.exceptions import ObjectDoesNotExist

from ..models import User
from core.decorators import authentication_required_query

EXTERNAL_USERS_PATTERN_FIELDS = ['full_name', 'nickname', 'email']
EXTERNAL_USERS_QUERYABLE_FIELDS = ('id', 'full_name', 'nickname', 'email')

class UserType(DjangoObjectType):
    class Meta:
        model = User
        exclude = ('password',)

class PatternFilter(graphene.InputObjectType):
    field = graphene.String()
    pattern = graphene.String()

class UserFilterOptions(graphene.InputObjectType):
    is_verified = graphene.Boolean()
    patterns = graphene.List(PatternFilter)

class ExternalUserType(DjangoObjectType):
    class Meta:
        model = User
        fields = EXTERNAL_USERS_QUERYABLE_FIELDS


class UsersQueries(graphene.ObjectType):
    user = graphene.Field(UserType, id = graphene.Int())
    get_users = graphene.Field(graphene.List(ExternalUserType), filter = UserFilterOptions())

    @authentication_required_query
    def resolve_user(root, info, id):
        try:
            user_record: User = User.objects.get(id = id)
            if info.context.get('user_id', None) != id:
                raise Exception('Cannot get an external user.')

            return user_record

        except ObjectDoesNotExist:
            return None
    
    @authentication_required_query
    def resolve_get_users(root, info, filter):
        filter = {} if filter is None else filter

        users = User.objects.exclude(id = info.context.get('user_id'))

        if filter.get('is_verified', None) is not None:
            users = users.filter(is_verified = filter['is_verified'])

        for pattern in filter.get('patterns', []):
            if pattern.get('field') is None or pattern.get('pattern') is None:
                continue

            pattern['field'] = humps.decamelize(pattern['field'])

            if not hasattr(User, pattern['field']) or pattern['field'] not in EXTERNAL_USERS_PATTERN_FIELDS:
                continue

            users = users.filter(**{ f'{pattern["field"]}__contains': pattern["pattern"]})
    
        return users
    