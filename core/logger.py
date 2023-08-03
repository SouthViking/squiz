import enum
from datetime import datetime
from typing import Union, TypedDict, List

class LogType(enum.IntEnum):
    DEBUG = 1
    INFO = 2
    WARN = 3
    ERROR = 4

class BufferConfig(TypedDict):
    max_logs: int
    target_types: List[LogType]

class LoggerConfig(TypedDict):
    buffer: Union[BufferConfig, None]

class Logger:
    def __init__(self, name: Union[str, None], config: LoggerConfig):
        self.config = config
        self.logs_buffer = []
        self.name = name or ''

    def generate_base_log(self, text: str, type: LogType) -> str:
        name_part = f'{self.name}: ' if len(self.name) != 0 else ''
        base_log = f'{name_part}({type.name}) [{datetime.now().replace(microsecond = 0)}] {text}'

        if self.config['buffer'] and type in self.config['buffer']['target_types']:
            self.store_log_in_buffer(base_log)

        return base_log

    def store_log_in_buffer(self, log: str):
        if len(self.logs_buffer) + 1 == self.config['buffer']['max_logs']:
            self.logs_buffer.append(log)
            # TODO: Export the lines to a file and clear the buffer. (Need a file manager class as attribute for this one)
            return
        
        self.logs_buffer.append(log)

    def debug(self, text: str) -> None:
        log = self.generate_base_log(text, LogType.DEBUG)
        print(log)

    def info(self, text: str) -> None:
        log = self.generate_base_log(text, LogType.INFO)
        print(log)
    
    def warn(self, text: str) -> None:
        log = self.generate_base_log(text, LogType.WARN)
        print(log)

    def error(self, text: str) -> None:
        log = self.generate_base_log(text, LogType.ERROR)
        print(log)

logger = Logger(None, { 'buffer': None })