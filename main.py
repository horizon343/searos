from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from db.context import get_db
from db.models.task_model import TaskCreate, Task, EveryPeriodEnum, StatusEnum
from db.models.base_model import Base
from db.context import engine
from celery_folder.celery_tasks import execute_task

Base.metadata.create_all(bind=engine)

app = FastAPI()
