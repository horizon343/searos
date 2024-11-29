from sqlalchemy import Column, Integer, String, DateTime, Enum
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import enum
from db.models.base_model import Base


class RequestTypeEnum(enum.Enum):
    SQL = "sql"
    API = "api"


class StatusEnum(enum.Enum):
    PAUSED = "paused"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class EveryPeriodEnum(enum.Enum):
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    NONE = "none"


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    request_type = Column(Enum(RequestTypeEnum), nullable=False)
    request = Column(String, nullable=False)
    every = Column(Enum(EveryPeriodEnum), nullable=False)
    period = Column(DateTime, nullable=False)
    status = Column(Enum(StatusEnum), nullable=False)


class TaskCreate(BaseModel):
    request_type: RequestTypeEnum
    request: str = Field(..., min_length=1)
    every: EveryPeriodEnum
    period: Optional[datetime]
    status: StatusEnum
