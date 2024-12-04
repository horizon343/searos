from sqladmin import ModelView, action
from starlette.requests import Request
from starlette.responses import RedirectResponse
from celery_folder.celery_tasks import celery_app, execute_task_sql
from db.context import SessionLocal
from db.models.base_model import StatusEnum
from db.models.task_sql_model import TaskSql
from start_task import start_task


class TaskSqlModelView(ModelView, model=TaskSql):
    can_create = True
    can_edit = False
    can_delete = True
    can_view_details = True
    can_export = True

    name = "tasks"
    name_plural = "tasks"
    icon = "fa-solid fa-database"
    category = "task sql"

    column_export_list = [TaskSql.id, TaskSql.connect_string, TaskSql.query, TaskSql.every,
                          TaskSql.period, TaskSql.status]
    export_types = ["csv", "json"]
    export_max_rows = 500

    form_columns = [TaskSql.connect_string, TaskSql.query, TaskSql.every, TaskSql.period,
                    TaskSql.status]

    column_list = [TaskSql.id, TaskSql.connect_string, TaskSql.query, TaskSql.every,
                   TaskSql.period, TaskSql.status]
    column_searchable_list = [TaskSql.id]
    column_sortable_list = [TaskSql.id, TaskSql.connect_string, TaskSql.every, TaskSql.period,
                            TaskSql.status]

    column_details_list = [TaskSql.id, TaskSql.connect_string, TaskSql.query, TaskSql.every,
                           TaskSql.period, TaskSql.status]

    page_size = 50
    page_size_options = [25, 50, 100, 200]

    @action(name="start_task_sql",
            label="Start tasks",
            confirmation_message="Вы точно хотите запустить эту задачу?",
            add_in_detail=True,
            add_in_list=True)
    async def start_task_sql(self, request: Request):
        db = SessionLocal()

        pks = request.query_params.get("pks", "").split(",")
        if pks:
            for pk in pks:
                task_sql: TaskSql = db.query(TaskSql).filter(TaskSql.id == pk).first()
                if not task_sql:
                    continue

                task_sql.status = StatusEnum.IN_PROGRESS
                db.commit()

                start_task(task_sql, db, execute_task_sql)

        db.close()

        referer = request.headers.get("Referer")
        return RedirectResponse(referer)

    @action(name="paused_task_sql",
            label="Pause tasks",
            confirmation_message="Вы точно хотите остановить эту задачу?",
            add_in_detail=True,
            add_in_list=True)
    async def paused_task_sql(self, request: Request):
        db = SessionLocal()

        pks = request.query_params.get("pks", "").split(",")
        if pks:
            for pk in pks:
                task_sql: TaskSql = db.query(TaskSql).filter(TaskSql.id == pk).first()
                if not task_sql:
                    continue

                celery_app.control.revoke(task_sql.task_celery_id, terminate=True,
                                          signal='SIGKILL')

                task_sql.status = StatusEnum.PAUSED
                task_sql.task_celery_id = None
                db.commit()

        db.close()

        referer = request.headers.get("Referer")
        return RedirectResponse(referer)

    async def after_model_change(self, data: dict, model: TaskSql, is_created: bool,
                                 request: Request):
        db = SessionLocal()

        task_sql: TaskSql = db.query(TaskSql).filter(TaskSql.id == model.id).first()

        if task_sql.status == StatusEnum.IN_PROGRESS:
            start_task(task_sql, db, execute_task_sql)

        db.close()

    async def on_model_delete(self, model: TaskSql, request: Request):
        db = SessionLocal()

        task_sql: TaskSql = db.query(TaskSql).filter(TaskSql.id == model.id).first()
        if not task_sql:
            return

        if task_sql.task_celery_id:
            celery_app.control.revoke(task_sql.task_celery_id, terminate=True, signal='SIGKILL')
