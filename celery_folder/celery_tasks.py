from celery import Celery
from celery.exceptions import Retry
import requests
from db.context import SessionLocal
from db.models.task_api_model import TaskApi, MethodEnum, TaskApiResult
from db.models.base_model import StatusEnum, ResultEnum

celery_app = Celery("celery_folder.celery_tasks", broker="redis://localhost:6379/0")


@celery_app.task(bind=True, max_retries=2, default_retry_delay=60 * 2)
def execute_task_api(self, task_api_id: int):
    db = SessionLocal()

    task_api = db.query(TaskApi).filter(TaskApi.id == task_api_id).first()
    if not task_api:
        return f"TaskApi with id {task_api_id} not found"

    task_api_result = TaskApiResult(task_api_id=task_api_id, status=ResultEnum.SUCCESSFULLY)

    try:

        print(f"Executing task {task_api_id} with method {task_api.method}")

        if task_api.method == MethodEnum.GET:
            response = requests.get(task_api.url)
        elif task_api.method == MethodEnum.POST:
            response = requests.post(task_api.url, json=task_api.body)

        if (response.status_code >= 200 and response.status_code <= 299):
            task_api.status = StatusEnum.COMPLETED
            task_api_result.status = ResultEnum.SUCCESSFULLY
            task_api_result.response_data = response.text

            print(f"TaskApi execution successful: {response.status_code}")

            return f"TaskApi execution successful: {response.status_code}"
        else:
            task_api_result.status = ResultEnum.FAILED

            print(f"TaskApi execution failed: {response.status_code}")

            raise Exception()

    except Exception as e:

        try:
            raise self.retry(exc=e, countdown=10)

        except Exception as e:
            if not isinstance(e, Retry):
                task_api.status = StatusEnum.FAILED

                print("Max retries exceeded")

        finally:
            db.add(task_api_result)
            db.commit()
            db.close()

    finally:
        db.add(task_api_result)
        db.commit()
        db.close()
