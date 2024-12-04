from sqladmin import ModelView
from db.models.task_api_model import TaskApiResult


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
    page_size_options = [25, 50, 100, 200]
