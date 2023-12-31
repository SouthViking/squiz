from datetime import datetime
from typing import Tuple, Union

def is_quiz_time_interval_valid(starts_at: datetime, ends_at: datetime, max_solving_mins: int) -> Tuple[bool, Union[str, None]]:
    starts_at = starts_at.replace(tzinfo = None)
    ends_at = ends_at.replace(tzinfo = None)

    if starts_at.replace() <= datetime.now():
        return (False, 'The start time cannot be less than the current time.')
    
    if ends_at <= datetime.now():
        return (False, 'The end time cannot be less than the current time.')
    
    if starts_at >= ends_at:
        return (False, 'End time must be greater than the start time.')
    
    max_solving_secs = max_solving_mins * 60
    full_solving_window_secs = (ends_at - starts_at).total_seconds()

    if max_solving_secs > full_solving_window_secs:
        return (False, f'Solving time is not valid. The maximum amount of minutes for the current interval is {int(full_solving_window_secs/60)} minutes ({max_solving_mins} specified).')
    
    return (True, None)

def is_solving_time_in_between_datetimes(starts_at: datetime, ends_at: datetime, solving_time_mins: int):
    return solving_time_mins <= int(((ends_at - starts_at).total_seconds()) / 60)