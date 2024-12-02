from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqladmin import Admin, ModelView, action
from authentication import AdminAuth
from db.context import get_db, engine
from db.models.base_model import Base, StatusEnum
from db.models.task_api_model import TaskApiCreate, TaskApi, TaskApiUpdate
from db.models.task_sql_model import TaskSqlCreate, TaskSql, TaskSqlUpdate
from db.models.user_model import User
from celery_folder.celery_tasks import execute_task_api, celery_app, execute_task_sql
from model_view.task_api_model_view import TaskApiModelView
from model_view.task_api_result_model_view import TaskApiResultModelView
from start_task import start_task

Base.metadata.create_all(bind=engine)

authentication_backend = AdminAuth(secret_key="super_secret_key")

app = FastAPI()
admin = Admin(app=app, engine=engine, authentication_backend=authentication_backend)


class UserAdmin(ModelView, model=User):
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True

    name = "User"
    name_plural = "Users"
    icon = "fa-solid fa-user"
    category = "accounts"

    column_list = [User.id, User.name, User.email, "user.address.zip_code"]
    column_searchable_list = [User.name]
    column_sortable_list = [User.id]
    column_formatters = {User.name: lambda m, a: m.name[:10]}
    column_default_sort = [(User.email, True), (User.name, False)]

    column_details_list = [User.id, User.name, "user.address.zip_code"]
    column_formatters_detail = {User.name: lambda m, a: m.name[:10]}

    page_size = 50
    page_size_options = [25, 50, 100, 200]

    @action(
        name="approve_users",
        label="Approve",
        confirmation_message="Are you sure?",
        add_in_detail=True,
        add_in_list=True,
    )
    async def approve_users(self, request):
        print("approve_users")


admin.add_view(UserAdmin)
admin.add_view(TaskApiModelView)
admin.add_view(TaskApiResultModelView)


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
