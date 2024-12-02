from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from db.models.base_model import Base, StatusEnum, ResultEnum


class TaskSql(Base):
    __tablename__ = "tasks_sql"

    id = Column(Integer, primary_key=True, index=True)
    task_celery_id = Column(String, nullable=True)
    connect_string = Column(String, nullable=False)
    query = Column(String, nullable=False)
    every = Column(Integer, default=0, nullable=False)
    period = Column(DateTime, nullable=False)
    status = Column(Enum(StatusEnum), nullable=False)

    results = relationship("TaskSqlResult", back_populates="task", cascade="all, delete-orphan")


class TaskSqlCreate(BaseModel):
    connect_string: str = Field(..., min_length=1)
    query: str = Field(..., min_length=1)
    every: int
    period: Optional[datetime]
    status: StatusEnum


class TaskSqlUpdate(BaseModel):
    connect_string: Optional[str] = None
    query: Optional[str] = None
    every: Optional[int] = None
    period: Optional[datetime] = None
    status: Optional[StatusEnum] = None


class TaskSqlResult(Base):
    __tablename__ = "tasks_sql_result"

    id = Column(Integer, primary_key=True, index=True)
    task_sql_id = Column(Integer, ForeignKey("tasks_sql.id", ondelete="CASCADE"), nullable=False)
    response_data = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now())
    status = Column(Enum(ResultEnum), nullable=False)

    task = relationship("TaskSql", back_populates="results")
