from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from pydantic import BaseModel, Field
from typing import Optional, Union, Dict, Any
from datetime import datetime
import enum
from db.models.base_model import Base, StatusEnum, ResultEnum, NotificationTypeEnum


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
    method = Column(Enum(MethodEnum), default=MethodEnum.GET, nullable=False)
    url = Column(String, nullable=False)
    body = Column(JSON, nullable=False)
    every = Column(Integer, default=0, nullable=False)
    period = Column(DateTime, default=datetime.now(), nullable=False)
    status = Column(Enum(StatusEnum), default=StatusEnum.IN_PROGRESS, nullable=False)
    notification_type = Column(Enum(NotificationTypeEnum), default=NotificationTypeEnum.NONE,
                               nullable=False)
    result_in_notification = Column(Boolean, default=False, nullable=False)
    notification_addr = Column(String, default=None, nullable=True)

    results = relationship("TaskApiResult", back_populates="task", cascade="all, delete-orphan")


class TaskApiCreate(BaseModel):
    method: MethodEnum
    url: str = Field(..., min_length=1)
    body: Union[Dict[str, Any], list]
    every: int = 0
    period: Optional[datetime]
    status: StatusEnum
    notification_type: NotificationTypeEnum
    result_in_notification: bool
    notification_addr: str


class TaskApiUpdate(BaseModel):
    status: Optional[StatusEnum] = None
    notification_type: Optional[NotificationTypeEnum] = None
    result_in_notification: Optional[bool] = None
    notification_addr: Optional[str] = None


class TaskApiResult(Base):
    __tablename__ = "tasks_api_result"

    id = Column(Integer, primary_key=True, index=True)
    task_api_id = Column(Integer, ForeignKey("tasks_api.id", ondelete="CASCADE"), nullable=False)
    response_data = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now())
    status = Column(Enum(ResultEnum), nullable=False)

    task = relationship("TaskApi", back_populates="results")
