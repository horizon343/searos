from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, JSON
from sqlalchemy.orm import relationship
from pydantic import BaseModel, Field
from typing import Optional, Union, Dict, Any
from datetime import datetime
import enum
from db.models.base_model import Base, StatusEnum, EveryPeriodEnum, ResultEnum


class MethodEnum(enum.Enum):
    POST = "post"
    GET = "get"
    PATCH = "patch"
    PUT = "put"
    DELETE = "delete"


class TaskApi(Base):
    __tablename__ = "tasks_api"

    id = Column(Integer, primary_key=True, index=True)
    task_celery_id = Column(String, nullable=True)
    method = Column(Enum(MethodEnum), nullable=False)
    url = Column(String, nullable=False)
    body = Column(JSON, nullable=False)
    every = Column(Enum(EveryPeriodEnum), nullable=False)
    period = Column(DateTime, nullable=False)
    status = Column(Enum(StatusEnum), nullable=False)

    results = relationship("TaskApiResult", back_populates="task", cascade="all, delete-orphan")


class TaskApiCreate(BaseModel):
    method: MethodEnum
    url: str = Field(..., min_length=1)
    body: Union[Dict[str, Any], list]
    every: EveryPeriodEnum
    period: Optional[datetime]
    status: StatusEnum


class TaskApiResult(Base):
    __tablename__ = "tasks_api_result"

    id = Column(Integer, primary_key=True, index=True)
    task_api_id = Column(Integer, ForeignKey("tasks_api.id", ondelete="CASCADE"), nullable=False)
    response_data = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now())
    status = Column(Enum(ResultEnum), nullable=False)

    task = relationship("TaskApi", back_populates="results")
