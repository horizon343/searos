from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from db.context import get_db
from db.models.base_model import Base, StatusEnum, EveryPeriodEnum
from db.context import engine
from db.models.task_api_model import TaskApiCreate, TaskApi
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
                task_celery_id = execute_task_api.apply_async(args=[new_task_api.id],
                                                              countdown=delay)
                new_task_api.task_celery_id = task_celery_id.id
                db.commit()
                print(f"Выполнение задачи через: {delay}")
            else:
                new_task_api.status = StatusEnum.PAUSED
                db.commit()
                print("У задачи прошло время выполнения, задача поставлена на паузу")
        else:
            print("Запуск задачи в цикле")

    return {"message": "Task added successfully"}
