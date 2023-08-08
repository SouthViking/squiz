import graphene

from .mutators import (
    QuizCreationMutation,
    QuizUpdateMutation,
    QuizReScheduleMutation,
    QuestionCreationMutation,
    QuestionUpdateMutation,
    QuestionDeleteMutation,
    AddOptionToQuestionMutation,
    SetCorrectOptionMutation,
    UserStartQuizMutation
)

class QuizMutations(graphene.ObjectType):
    create_quiz = QuizCreationMutation.Field()
    update_quiz = QuizUpdateMutation.Field()
    reschedule_quiz = QuizReScheduleMutation.Field()
    user_start_quiz = UserStartQuizMutation.Field()

    create_question = QuestionCreationMutation.Field()
    update_question = QuestionUpdateMutation.Field()
    delete_question = QuestionDeleteMutation.Field()

    add_option_to_question = AddOptionToQuestionMutation.Field()
    set_correct_option = SetCorrectOptionMutation.Field()