from celery import Celery
from celery.exceptions import Retry
import requests
from db.context import SessionLocal
from db.models.task_api_model import TaskApi, TaskApiResult
from db.models.base_model import StatusEnum, ResultEnum

celery_app = Celery("celery_folder.celery_tasks", broker="redis://localhost:6379/0")


@celery_app.task(bind=True, max_retries=2, default_retry_delay=60 * 2)
def execute_task_api(self, task_api_id: int, every: int):
    db = SessionLocal()

    task_api = db.query(TaskApi).filter(TaskApi.id == task_api_id).first()
    if not task_api:
        return f"TaskApi with id {task_api_id} not found"

    task_api_result = TaskApiResult(task_api_id=task_api_id, status=ResultEnum.SUCCESSFULLY)

    try:
        print(f"Executing task {task_api_id} with method {task_api.method}")

        http_method = task_api.method.value.lower()
        method_func = getattr(requests, http_method, None)
        if not method_func:
            raise ValueError(f"Unsupported HTTP method: {task_api.method}")

        if task_api.body:
            response = method_func(task_api.url, json=task_api.body)
        else:
            response = method_func(task_api.url)

        if 200 <= response.status_code <= 299:
            if every == 0:
                task_api.status = StatusEnum.COMPLETED
                task_api.task_celery_id = None
            else:
                task_api.status = StatusEnum.IN_PROGRESS

            task_api_result.status = ResultEnum.SUCCESSFULLY
            task_api_result.response_data = response.text

            print(f"TaskApi execution successful: {response.status_code}")

            return f"TaskApi execution successful: {response.status_code}"
        else:
            task_api_result.status = ResultEnum.FAILED
            task_api_result.response_data = response.status_code

            print(f"TaskApi execution failed: {response.status_code}")

            raise Exception()

    except Exception as e:
        try:
            if every == 0:
                raise self.retry(exc=e, countdown=20)

        except Exception as e:
            if not isinstance(e, Retry):
                task_api.status = StatusEnum.FAILED
                task_api.task_celery_id = None

                print("Max retries exceeded")

    finally:
        if every != 0:
            task_celery_id = self.apply_async(args=[task_api_id, every], countdown=every)
            task_api.task_celery_id = task_celery_id.id

        db.add(task_api_result)
        db.commit()
        db.close()
