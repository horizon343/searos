from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from db.context import get_db
from db.models.base_model import Base, StatusEnum, EveryPeriodEnum, ResultEnum
from db.context import engine
from db.models.task_api_model import TaskApiCreate, TaskApi, TaskApiResult
from celery_folder.celery_tasks import execute_task_api

Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.post("/add_task_api")
def add_task(data: TaskApiCreate, db: Session = Depends(get_db)):
    new_task_api = TaskApi(method=data.method, url=data.url, body=data.body,
                           every=data.every, period=data.period, status=data.status)
    db.add(new_task_api)
    db.commit()

    if data.status == StatusEnum.IN_PROGRESS:
        if data.every == EveryPeriodEnum.NONE:
            now = datetime.now()

            if data.period > now:
                delay = (data.period - now).total_seconds()
                execute_task_api.apply_async(args=[new_task_api.id], countdown=5)
                print("Выполнение задачи через заданное время")
            else:
                new_task_api.status = StatusEnum.PAUSED
                db.commit()
                print("У задачи прошло время выполнения, задача поставлена на паузу")
        else:
            print("Запуск задачи в цикле по дням или часам")

    return {"message": "Task added successfully"}
