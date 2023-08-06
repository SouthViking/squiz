from enum import IntEnum
from datetime import datetime
from typing import TypedDict, Callable, List, Dict, Any

class JobType(IntEnum):
    INTERVAL = 0
    DATETIME = 1

class JobDefinition(TypedDict):
    id: str
    name: str
    func: Callable
    args: List[Any]
    kwargs: Dict[str, Any]

class IntervalJobDefinition(JobDefinition):
    seconds: int

class DateTimeBasedJobDefinition(JobDefinition):
    run_date: datetime

class JobDefinitionsPerType(TypedDict):
    interval_jobs: List[IntervalJobDefinition]
    datetime_jobs: List[DateTimeBasedJobDefinition]

class AppJobsConfig(TypedDict):
    on_start_up_jobs: JobDefinitionsPerType
    on_start_up_callbacks: List[Callable]