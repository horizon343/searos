from fastapi import FastAPI, Depends
import os
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from sqladmin import Admin
from authentication import AdminAuth
from db.context import get_db, engine, SessionLocal
from db.models.base_model import Base, StatusEnum
from db.models.task_api_model import TaskApiCreate, TaskApi, TaskApiUpdate
from db.models.task_sql_model import TaskSqlCreate, TaskSql, TaskSqlUpdate
from db.models.user_model import User
from model_view.task_api_model_view import TaskApiModelView
from model_view.task_sql_model_view import TaskSqlModelView
from model_view.task_api_result_model_view import TaskApiResultModelView
from model_view.task_sql_result_model_view import TaskSqlResultModelView
from model_view.user_admin_model_view import UserAdmin
from celery_folder.celery_tasks import execute_task_api, celery_app, execute_task_sql
from start_task import start_task

load_dotenv()
secret_key = os.environ["ADMIN_AUTH_SECRET_KEY"]

Base.metadata.create_all(bind=engine)

authentication_backend = AdminAuth(secret_key=secret_key)

app = FastAPI()
admin = Admin(app=app, engine=engine, authentication_backend=authentication_backend)

admin.add_view(UserAdmin)
admin.add_view(TaskApiModelView)
admin.add_view(TaskApiResultModelView)
admin.add_view(TaskSqlModelView)
admin.add_view(TaskSqlResultModelView)


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


@app.patch("/update_task_sql/{task_sql_id}")
def update_task_sql(task_sql_id: int, task_sql_data: TaskSqlUpdate, db: Session = Depends(get_db)):
    task_sql = db.query(TaskSql).filter(TaskSql.id == task_sql_id).first()
    if not task_sql:
        return {"message": "Task not found"}

    update_task_data = task_sql_data.dict(exclude_unset=True)
    for key, value in update_task_data.items():
        setattr(task_sql, key, value)

    if task_sql.task_celery_id:
        celery_app.control.revoke(task_sql.task_celery_id, terminate=True, signal='SIGKILL')
        task_sql.task_celery_id = None

    db.commit()

    if task_sql.status == StatusEnum.IN_PROGRESS:
        start_task(task_sql, db, execute_task_sql)

    return {"message": "Task updated successfully"}


@app.delete("/delete_task_sql/{task_sql_id}")
def delete_task_sql(task_sql_id: int, db: Session = Depends(get_db)):
    task_sql = db.query(TaskSql).filter(TaskSql.id == task_sql_id).first()
    if not task_sql:
        return {"message": "Task not found"}

    if task_sql.task_celery_id:
        celery_app.control.revoke(task_sql.task_celery_id, terminate=True, signal='SIGKILL')

    db.delete(task_sql)
    db.commit()

    return {"message": f"Task deleted successfully"}


def add_admin():
    db = SessionLocal()

    admin_user: User = User(name="admin", password="admin")
    admin_db = db.query(User).filter(User.name == admin_user.name).first()
    if not admin_db:
        db.add(admin_user)
    db.commit()
    db.close()


add_admin()
