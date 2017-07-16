from celery.task import task
from celery.task import PeriodicTask
from celery.task.base import periodic_task
import celery
import time
import datetime
from elasticsearch import Elasticsearch
from main.upload_file_into_es import upload_file_into_es


@task(ignore_result = True, max_retries = 1, default_retry_delay = 10)
def just_print():
    time.sleep(10)
    print('---------------HELLO WORLD!!!!!-------------')


# @periodic_task(run_every = datetime.timedelta(seconds = 4))
# def another_print():
#     print('Another HELLO WORLD!!!!!')

# class TestPeriodic(PeriodicTask):
#     run_every = datetime.timedelta(seconds=2)
#
#     def run(self, **kwargs):
#         logger = self.get_logger(**kwargs)
#         logger.info("Running periodic task!")
#         print('sadfasdfasdfsdfas')

# (ignore_result = True)
@task
def put_data_in_es(index_name, doc_type, file_path):
    # es = Elasticsearch()
    # mapping = \
    #     {
    #         "properties": {
    #             "row": {"type": "long"},
    #             "col": {"type": "long"},
    #             "orig_value": {"type": "text", "fields": {"raw_value": {"type": "keyword"}}}
    #         }
    #     }
    # es.indices.create(index = index_name)
    # es.indices.put_mapping(index = index_name, doc_type = doc_type, body = mapping)
    # time.sleep(1.5)
    # upload_file_into_es(file_path = file_path, index_name = index_name)
    time.sleep(1)
    print('DONE!!!!!!!!!')