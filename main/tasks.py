# from celery.task.schedules import crontab
# from celery.decorators import periodic_task
# from main import test_periodic_task
# from celery.utils.log import get_task_logger
# import datetime
# import celery

from celery.task import task


@task(ignore_result=True, max_retries=1, default_retry_delay=10)
def just_print():
    print('HELLO WORLD!!!!!')


@task(ignore_result=True, max_retries=1, default_retry_delay=10)
def another_print():
    print('Another HELLO WORLD!!!!!')
