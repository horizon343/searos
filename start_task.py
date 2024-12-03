from datetime import datetime
from db.models.base_model import StatusEnum


def start_task(new_task, db, execute_task):
    if new_task.every == 0:
        now = datetime.now()

        if new_task.period > now:
            delay = (new_task.period - now).total_seconds()

            task_celery_id = execute_task.apply_async(args=[new_task.id, new_task.every],
                                                      countdown=delay)
            new_task.task_celery_id = task_celery_id.id

            db.commit()
            print(f"Выполнение задачи через: {delay}")
        else:
            new_task.status = StatusEnum.PAUSED

            db.commit()
            print("У задачи прошло время выполнения, задача поставлена на паузу")
    else:
        task_celery_id = execute_task.apply_async(args=[new_task.id, new_task.every],
                                                  countdown=new_task.every)
        new_task.task_celery_id = task_celery_id.id

        db.commit()
        print("Запуск задачи в цикле")
