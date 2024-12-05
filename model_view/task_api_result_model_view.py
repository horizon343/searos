from sqladmin import ModelView, action
from starlette.responses import JSONResponse
from starlette.requests import Request
from db.models.task_api_model import TaskApiResult
from db.context import SessionLocal


class TaskApiResultModelView(ModelView, model=TaskApiResult):
    @staticmethod
    def _shorten_response_data(m, a):
        return m.response_data[:150] + "..." if len(m.response_data) > 150 else m.response_data

    can_create = False
    can_edit = False
    can_delete = True
    can_view_details = True
    can_export = True

    name = "tasks result"
    name_plural = "tasks result"
    icon = "fa-solid fa-square-poll-vertical"
    category = "task api"

    column_export_list = [TaskApiResult.id, TaskApiResult.task_api_id, TaskApiResult.response_data,
                          TaskApiResult.created_at, TaskApiResult.status]
    export_types = ["csv", "json"]
    export_max_rows = 500

    column_list = [TaskApiResult.id, TaskApiResult.task_api_id, TaskApiResult.response_data,
                   TaskApiResult.created_at, TaskApiResult.status]
    column_formatters = {TaskApiResult.response_data: _shorten_response_data}

    column_searchable_list = [TaskApiResult.task_api_id]
    column_sortable_list = [TaskApiResult.id, TaskApiResult.task_api_id, TaskApiResult.created_at,
                            TaskApiResult.status]

    column_details_list = [TaskApiResult.task, TaskApiResult.id, TaskApiResult.task_api_id,
                           TaskApiResult.response_data, TaskApiResult.created_at,
                           TaskApiResult.status]

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

        tasks = db.query(TaskApiResult).filter(TaskApiResult.id.in_(pks)).all()
        db.close()

        data = [
            {
                "id": task.id,
                "task_api_id": task.task_api_id,
                "response_data": task.response_data,
                "created_at": task.created_at.isoformat() if task.created_at else None,
                "status": task.status.value
            }
            for task in tasks
        ]

        return JSONResponse(
            content={"tasks_result": data},
            media_type="application/json",
            headers={"Content-Disposition": "attachment; filename=tasks_api_result.json"})
