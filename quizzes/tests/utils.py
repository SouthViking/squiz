from django.test import TestCase
from datetime import datetime, timedelta

from quizzes.utils import is_quiz_time_interval_valid

class QuizUtilsTests(TestCase):
    def test_is_quiz_time_interval_valid(self):
        starts_at = datetime.now() - timedelta(days = 2)
        ends_at = datetime.now() + timedelta(days = 1)

        # Setting max_solving_mins as 1, since it is not being tested here.
        is_valid, error_message = is_quiz_time_interval_valid(starts_at, ends_at, 1)
        self.assertFalse(is_valid)
        self.assertEqual(error_message, 'The start time cannot be less than the current time.')

        starts_at = datetime.now() + timedelta(seconds= 10)
        ends_at = datetime.now() - timedelta(days = 2)

        is_valid, error_message = is_quiz_time_interval_valid(starts_at, ends_at, 1)
        self.assertFalse(is_valid)
        self.assertEqual(error_message, 'The end time cannot be less than the current time.')

        starts_at = datetime.now() + timedelta(minutes = 2)
        ends_at = datetime.now() + timedelta(minutes = 1)

        is_valid, error_message = is_quiz_time_interval_valid(starts_at, ends_at, 1)
        self.assertFalse(is_valid)
        self.assertEqual(error_message, 'End time must be greater than the start time.')

        starts_at = datetime.now() + timedelta(hours = 1)
        ends_at = starts_at + timedelta(hours = 4)

        max_expected_window_mins = int((ends_at - starts_at).total_seconds()/60)
        wrong_window_mins = max_expected_window_mins + 1

        is_valid, error_message = is_quiz_time_interval_valid(starts_at, ends_at, wrong_window_mins)
        self.assertFalse(is_valid)
        self.assertEqual(error_message, f'Solving time is not valid. The maximum amount of minutes for the current interval is {max_expected_window_mins} minutes ({wrong_window_mins} specified).')

        is_valid, error_message = is_quiz_time_interval_valid(starts_at, ends_at, max_expected_window_mins)
        self.assertTrue(is_valid)
        self.assertEqual(error_message, None)