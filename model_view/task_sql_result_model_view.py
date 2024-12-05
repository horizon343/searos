from sqladmin import ModelView, action
from starlette.requests import Request
from starlette.responses import JSONResponse
import json
from db.context import SessionLocal
from db.models.task_sql_model import TaskSqlResult


class TaskSqlResultModelView(ModelView, model=TaskSqlResult):
    @staticmethod
    def _shorten_response_data(m, a):
        return m.response_data[:150] + "..." if len(
            str(m.response_data)) > 150 else m.response_data

    can_create = False
    can_edit = False
    can_delete = True
    can_view_details = True
    can_export = True

    name = "tasks result"
    name_plural = "tasks result"
    icon = "fa-solid fa-square-poll-vertical"
    category = "task sql"

    column_export_list = [TaskSqlResult.id, TaskSqlResult.task_sql_id, TaskSqlResult.response_data,
                          TaskSqlResult.created_at, TaskSqlResult.status]
    export_types = ["csv", "json"]
    export_max_rows = 500

    column_list = [TaskSqlResult.id, TaskSqlResult.task_sql_id, TaskSqlResult.response_data,
                   TaskSqlResult.created_at, TaskSqlResult.status]
    column_formatters = {TaskSqlResult.response_data: _shorten_response_data}

    column_searchable_list = [TaskSqlResult.task_sql_id]
    column_sortable_list = [TaskSqlResult.id, TaskSqlResult.task_sql_id, TaskSqlResult.created_at,
                            TaskSqlResult.status]

    column_details_list = [TaskSqlResult.task, TaskSqlResult.id, TaskSqlResult.task_sql_id,
                           TaskSqlResult.response_data, TaskSqlResult.created_at,
                           TaskSqlResult.status]

    page_size = 50
    page_size_options = [25, 50, 100, 200, 500, 1000]

    @action(name="export_to_json",
            label="Export to JSON",
            confirmation_message="Вы точно хотите экспортировать выбранные результаты задач?",
            add_in_detail=True,
            add_in_list=True)
    async def export_to_json(self, request: Request):
        db = SessionLocal()

        pks = request.query_params.get("pks", "").split(",")
        if not pks:
            db.close()
            return JSONResponse({"error": "No tasks_result selected for export"}, status_code=400)

        tasks = db.query(TaskSqlResult).filter(TaskSqlResult.id.in_(pks)).all()
        db.close()

        data = [
            {
                "id": task.id,
                "task_sql_id": task.task_sql_id,
                "response_data": json.loads(task.response_data) if task.response_data else None,
                "created_at": task.created_at.isoformat() if task.created_at else None,
                "status": task.status.value
            }
            for task in tasks
        ]

        return JSONResponse(
            content={"tasks_result": data},
            media_type="application/json",
            headers={"Content-Disposition": "attachment; filename=tasks_sql_result.json"})
