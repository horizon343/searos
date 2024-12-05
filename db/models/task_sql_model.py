from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from db.models.base_model import Base, StatusEnum, ResultEnum, NotificationTypeEnum


class TaskSql(Base):
    __tablename__ = "tasks_sql"

    id = Column(Integer, primary_key=True, index=True)
    task_celery_id = Column(String, nullable=True)
    connect_string = Column(String, nullable=False)
    query = Column(String, nullable=False)
    every = Column(Integer, default=0, nullable=False)
    period = Column(DateTime, default=datetime.now(), nullable=False)
    status = Column(Enum(StatusEnum), default=StatusEnum.IN_PROGRESS, nullable=False)
    notification_type = Column(Enum(NotificationTypeEnum), default=NotificationTypeEnum.NONE,
                               nullable=False)
    result_in_notification = Column(Boolean, default=False, nullable=False)
    notification_addr = Column(String, default=None, nullable=True)

    results = relationship("TaskSqlResult", back_populates="task", cascade="all, delete-orphan")


class TaskSqlCreate(BaseModel):
    connect_string: str = Field(..., min_length=1)
    query: str = Field(..., min_length=1)
    every: int
    period: Optional[datetime]
    status: StatusEnum
    notification_type: NotificationTypeEnum
    result_in_notification: bool
    notification_addr: str


class TaskSqlUpdate(BaseModel):
    status: Optional[StatusEnum] = None
    notification_type: Optional[NotificationTypeEnum] = None
    result_in_notification: Optional[bool] = None
    notification_addr: Optional[str] = None


class TaskSqlResult(Base):
    __tablename__ = "tasks_sql_result"

    id = Column(Integer, primary_key=True, index=True)
    task_sql_id = Column(Integer, ForeignKey("tasks_sql.id", ondelete="CASCADE"), nullable=False)
    response_data = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now())
    status = Column(Enum(ResultEnum), nullable=False)

    task = relationship("TaskSql", back_populates="results")
