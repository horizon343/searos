from sqlalchemy.orm import DeclarativeBase
import enum


class Base(DeclarativeBase): pass


class StatusEnum(enum.Enum):
    PAUSED = "paused"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class ResultEnum(enum.Enum):
    SUCCESSFULLY = "successfully"
    FAILED = "failed"
