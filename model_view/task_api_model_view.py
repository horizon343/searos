from sqladmin import ModelView, action
import json
from starlette.responses import JSONResponse
from starlette.requests import Request
from starlette.responses import RedirectResponse
from celery_folder.celery_tasks import execute_task_api, celery_app
from db.context import SessionLocal
from db.models.base_model import StatusEnum
from db.models.task_api_model import TaskApi
from start_task import start_task


class TaskApiModelView(ModelView, model=TaskApi):
    can_create = True
    can_edit = False
    can_delete = True
    can_view_details = True
    can_export = True

    name = "tasks"
    name_plural = "tasks"
    icon = "fa-brands fa-quinscape"
    category = "task api"

    form_columns = [TaskApi.method, TaskApi.url, TaskApi.body, TaskApi.every, TaskApi.period,
                    TaskApi.status, TaskApi.notification_type, TaskApi.result_in_notification,
                    TaskApi.notification_addr]

    column_export_list = [TaskApi.id, TaskApi.method, TaskApi.url, TaskApi.body, TaskApi.every,
                          TaskApi.period, TaskApi.status, TaskApi.notification_type,
                          TaskApi.result_in_notification, TaskApi.notification_addr]
    export_types = ["csv", "json"]
    export_max_rows = 500

    column_list = [TaskApi.id, TaskApi.method, TaskApi.url, TaskApi.body, TaskApi.every,
                   TaskApi.period, TaskApi.status, TaskApi.notification_type,
                   TaskApi.result_in_notification, TaskApi.notification_addr]
    column_searchable_list = [TaskApi.id]
    column_sortable_list = [TaskApi.id, TaskApi.method, TaskApi.url, TaskApi.every, TaskApi.period,
                            TaskApi.status, TaskApi.notification_type,
                            TaskApi.result_in_notification, TaskApi.notification_addr]

    column_details_list = [TaskApi.id, TaskApi.method, TaskApi.url, TaskApi.body, TaskApi.every,
                           TaskApi.period, TaskApi.status, TaskApi.notification_type,
                           TaskApi.result_in_notification, TaskApi.notification_addr]

    page_size = 50
    page_size_options = [25, 50, 100, 200, 500, 1000]

    @action(name="start_task_api",
            label="Start tasks",
            confirmation_message="Вы точно хотите запустить эту задачу?",
            add_in_detail=True,
            add_in_list=True)
    async def start_task_api(self, request: Request):
        db = SessionLocal()

        pks = request.query_params.get("pks", "").split(",")
        if pks:
            for pk in pks:
                task_api: TaskApi = db.query(TaskApi).filter(TaskApi.id == pk).first()
                if not task_api:
                    continue

                task_api.status = StatusEnum.IN_PROGRESS
                db.commit()

                start_task(task_api, db, execute_task_api)

        db.close()

        referer = request.headers.get("Referer")
        return RedirectResponse(referer)

    @action(name="paused_task_api",
            label="Pause tasks",
            confirmation_message="Вы точно хотите остановить эту задачу?",
            add_in_detail=True,
            add_in_list=True)
    async def paused_task_api(self, request: Request):
        db = SessionLocal()

        pks = request.query_params.get("pks", "").split(",")
        if pks:
            for pk in pks:
                task_api: TaskApi = db.query(TaskApi).filter(TaskApi.id == pk).first()
                if not task_api:
                    continue

                celery_app.control.revoke(task_api.task_celery_id, terminate=True,
                                          signal='SIGKILL')

                task_api.status = StatusEnum.PAUSED
                task_api.task_celery_id = None
                db.commit()

        db.close()

        referer = request.headers.get("Referer")
        return RedirectResponse(referer)

    @action(name="export_to_json",
            label="Export to JSON",
            confirmation_message="Вы точно хотите экспортировать выбранные задачи?",
            add_in_detail=True,
            add_in_list=True)
    async def export_to_json(self, request: Request):
        db = SessionLocal()

        pks = request.query_params.get("pks", "").split(",")
        if not pks:
            db.close()
            return JSONResponse({"error": "No tasks selected for export"}, status_code=400)

        tasks = db.query(TaskApi).filter(TaskApi.id.in_(pks)).all()
        db.close()

        data = [
            {
                "id": task.id,
                "method": task.method.value,
                "url": task.url,
                "body": task.body,
                "every": task.every,
                "period": task.period.isoformat() if task.period else None,
                "status": task.status.value,
                "notification_type": task.notification_type.value,
                "result_in_notification": task.result_in_notification,
                "notification_addr": task.notification_addr
            }
            for task in tasks
        ]

        return JSONResponse(
            content={"tasks": data},
            media_type="application/json",
            headers={"Content-Disposition": "attachment; filename=tasks_api.json"})

    async def after_model_change(self, data: dict, model: TaskApi, is_created: bool,
                                 request: Request):
        db = SessionLocal()

        task_api: TaskApi = db.query(TaskApi).filter(TaskApi.id == model.id).first()

        if task_api.status == StatusEnum.IN_PROGRESS:
            start_task(task_api, db, execute_task_api)

        db.close()

    async def on_model_delete(self, model: TaskApi, request: Request):
        db = SessionLocal()

        task_api: TaskApi = db.query(TaskApi).filter(TaskApi.id == model.id).first()
        if not task_api:
            return

        if task_api.task_celery_id:
            celery_app.control.revoke(task_api.task_celery_id, terminate=True, signal='SIGKILL')
