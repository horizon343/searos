from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from db.context import get_db, engine
from db.models.base_model import Base, StatusEnum
from db.models.task_api_model import TaskApiCreate, TaskApi, TaskApiUpdate
from db.models.task_sql_model import TaskSqlCreate, TaskSql
from celery_folder.celery_tasks import execute_task_api, celery_app, execute_task_sql

Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.post("/add_task_api")
def add_task_api(data: TaskApiCreate, db: Session = Depends(get_db)):
    new_task_api = TaskApi(method=data.method, url=data.url, body=data.body, every=data.every,
                           period=data.period, status=data.status)
    db.add(new_task_api)
    db.commit()

    if data.status == StatusEnum.IN_PROGRESS:
        start_task(new_task_api, db, execute_task_api)

    return {"message": "Task added successfully"}


@app.patch("/update_task_api/{task_api_id}")
def update_task_api(task_api_id: int, task_api_data: TaskApiUpdate, db: Session = Depends(get_db)):
    task_api = db.query(TaskApi).filter(TaskApi.id == task_api_id).first()
    if not task_api:
        return {"message": "Task not found"}

    update_task_data = task_api_data.dict(exclude_unset=True)
    for key, value in update_task_data.items():
        setattr(task_api, key, value)

    if task_api.task_celery_id:
        celery_app.control.revoke(task_api.task_celery_id, terminate=True, signal='SIGKILL')
        task_api.task_celery_id = None

    db.commit()

    if task_api.status == StatusEnum.IN_PROGRESS:
        start_task(task_api, db, execute_task_api)

    return {"message": "Task updated successfully"}


@app.delete("/delete_task_api/{task_api_id}")
def delete_task_api(task_api_id: int, db: Session = Depends(get_db)):
    task_api = db.query(TaskApi).filter(TaskApi.id == task_api_id).first()
    if not task_api:
        return {"message": "Task not found"}

    if task_api.task_celery_id:
        celery_app.control.revoke(task_api.task_celery_id, terminate=True, signal='SIGKILL')

    db.delete(task_api)
    db.commit()

    return {"message": f"Task deleted successfully"}


@app.post("/add_task_sql")
def add_task_sql(data: TaskSqlCreate, db: Session = Depends(get_db)):
    new_task_sql = TaskSql(connect_string=data.connect_string, query=data.query, every=data.every,
                           period=data.period, status=data.status)
    db.add(new_task_sql)
    db.commit()

    if data.status == StatusEnum.IN_PROGRESS:
        start_task(new_task_sql, db, execute_task_sql)

    return {"message": "Task added successfully"}


def start_task(new_task, db, execute_task):
    if new_task.every == 0:
        now = datetime.now()

        if new_task.period > now:
            delay = (new_task.period - now).total_seconds()

            task_celery_id = execute_task.apply_async(args=[new_task.id, new_task.every],
                                                      countdown=delay)
            new_task.task_celery_id = task_celery_id.id

            db.commit()
            print(f"Выполнение задачи через: {delay}")
        else:
            new_task.status = StatusEnum.PAUSED

            db.commit()
            print("У задачи прошло время выполнения, задача поставлена на паузу")
    else:
        task_celery_id = execute_task.apply_async(args=[new_task.id, new_task.every],
                                                  countdown=new_task.every)
        new_task.task_celery_id = task_celery_id.id

        db.commit()
        print("Запуск задачи в цикле")
