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
    UserStartQuizMutation,
    SubmitQuizAnswersMutation
)

from .queries import (
    QuizQueries as InternalQuizQueries,
    QuestionQueries,
    OptionQueries,
)

class QuizMutations(graphene.ObjectType):
    create_quiz = QuizCreationMutation.Field()
    update_quiz = QuizUpdateMutation.Field()
    reschedule_quiz = QuizReScheduleMutation.Field()
    user_start_quiz = UserStartQuizMutation.Field()
    submit_quiz_answers = SubmitQuizAnswersMutation.Field()

    create_question = QuestionCreationMutation.Field()
    update_question = QuestionUpdateMutation.Field()
    delete_question = QuestionDeleteMutation.Field()

    add_option_to_question = AddOptionToQuestionMutation.Field()
    set_correct_option = SetCorrectOptionMutation.Field()

class QuizQueries(InternalQuizQueries, QuestionQueries, OptionQueries):
    pass