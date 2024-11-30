from sqlalchemy import Column, Integer, String, DateTime, Enum
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from db.models.base_model import Base, StatusEnum, EveryPeriodEnum


class TaskSql(Base):
    __tablename__ = "tasks_sql"

    id = Column(Integer, primary_key=True, index=True)
    connect_string = Column(String, nullable=False)
    query = Column(String, nullable=False)
    every = Column(Enum(EveryPeriodEnum), nullable=False)
    period = Column(DateTime, nullable=False)
    status = Column(Enum(StatusEnum), nullable=False)


class TaskApiCreate(BaseModel):
    connect_string: str = Field(..., min_length=1)
    query: str = Field(..., min_length=1)
    every: EveryPeriodEnum
    period: Optional[datetime]
    status: StatusEnum
