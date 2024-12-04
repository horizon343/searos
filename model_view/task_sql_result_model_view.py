from sqladmin import ModelView
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
    page_size_options = [25, 50, 100, 200]
