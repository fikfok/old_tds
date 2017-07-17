from celery.task import task
from celery.task import PeriodicTask
from celery.task.base import periodic_task
import celery
import time
import datetime
from elasticsearch import Elasticsearch
from main.upload_file_into_es import upload_file_into_es
from main.models import UploadedFiles

@task(ignore_result = True, max_retries = 1, default_retry_delay = 10)
def just_print():
    time.sleep(10)
    print('---------------HELLO WORLD!!!!!-------------')


@task
def put_data_in_es(index_name, doc_type, file_path, read_chunk_size, parallel_jobs_count, index_chunk_size):
    time_creation = time.time()
    es = Elasticsearch()
    mapping = \
        {
            "properties": {
                "row": {"type": "long"},
                "col": {"type": "long"},
                "orig_value": {"type": "text", "fields": {"raw_value": {"type": "keyword"}}}
            }
        }
    es.indices.create(index = index_name)
    es.indices.put_mapping(index = index_name, doc_type = doc_type, body = mapping)
    time.sleep(1.5)

    time_indexing = time.time()
    upload_file_into_es(file_path = file_path,
                        index_name = index_name,
                        read_chunk_size = read_chunk_size,
                        parallel_jobs_count = parallel_jobs_count,
                        index_chunk_size = index_chunk_size)
    stop_time = time.time()
    current_file = UploadedFiles.objects.get(pk = index_name)
    current_file.upload_into_es_settings_rcs = read_chunk_size
    current_file.upload_into_es_settings_pp = parallel_jobs_count
    current_file.upload_into_es_settings_ics = index_chunk_size
    current_file.upload_into_es_ttm = stop_time - time_creation
    current_file.upload_into_es_itm = stop_time - time_indexing
    current_file.save()
