from typing import TypedDict, Callable, List, Dict, Any

class JobDefinition(TypedDict):
    id: str
    name: str
    func: Callable
    args: List[Any]
    kwargs: Dict[str, Any]

class IntervalJobDefinition(JobDefinition, TypedDict):
    seconds: int