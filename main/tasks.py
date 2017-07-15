from celery.task import task
from celery.task import PeriodicTask

import celery
import time
import datetime


@task(ignore_result=True, max_retries=1, default_retry_delay=10)
def just_print():
    # time.sleep(4)
    print('HELLO WORLD!!!!!')


@task(ignore_result=True, max_retries=1, default_retry_delay=10)
def another_print():
    print('Another HELLO WORLD!!!!!')


class TestPeriodic(PeriodicTask):
    run_every = datetime.timedelta(seconds=2)

    def run(self, **kwargs):
        logger = self.get_logger(**kwargs)
        logger.info("Running periodic task!")
        print('sadfasdfasdfsdfas')
