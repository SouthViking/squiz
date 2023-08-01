import graphene

class FieldUpdateErrorInfo(graphene.ObjectType):
    field = graphene.String()
    error = graphene.String()

class BaseMutationResult:
    success = graphene.Boolean()
    message = graphene.String()
    internal_message = graphene.String()