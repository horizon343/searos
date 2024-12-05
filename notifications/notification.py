from db.models.base_model import NotificationTypeEnum
from db.models.task_api_model import TaskApiResult, TaskApi
from notifications.email_notification import send_email


def notification_send(task_api: TaskApi, task_api_result: TaskApiResult):
    if task_api.notification_type == NotificationTypeEnum.EMAIL:
        message_text = f"Task {task_api.id} completed {task_api_result.status}\n{task_api_result.response_data if task_api.result_in_notification else ''}"
        send_email(task_api.notification_addr, "Task notification", message_text)
