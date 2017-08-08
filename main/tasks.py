from celery.task import task
from celery.task import PeriodicTask
from celery.task.base import periodic_task
import celery
import time
import datetime
from elasticsearch import Elasticsearch
from main.upload_file_into_es import upload_file_into_es
from main.models import UploadedFiles
from django.utils.timezone import now as django_now

@task(ignore_result = True, max_retries = 1, default_retry_delay = 10)
def just_print():
    time.sleep(10)
    print('---------------HELLO WORLD!!!!!-------------')


@task
def put_data_in_es(index_name, file_path, read_chunk_size, parallel_jobs_count, index_chunk_size, delimeter):
    current_file = UploadedFiles.objects.get(pk = index_name)

    time_creation = time.time()
    wait_time = 4
    es = Elasticsearch()

    columns = {'col_' + str(item): {"type": "string", "index": "not_analyzed"} for item in range(current_file.upload_into_es_cols_count)}
    columns['row_num'] = {"type": "long"}

    mapping = {'properties':
                    {
                    'col_' + str(item): {'type': 'string', 'index': 'not_analyzed'} for item in range(current_file.upload_into_es_cols_count)
                    }
                }

    mapping['properties']['row_num'] = {'type': 'long'}

    es.indices.create(index = index_name)
    es.indices.put_mapping(index = index_name, doc_type = index_name, body = mapping)

    t0 = time.time()
    while not es.indices.exists_type(index = index_name, doc_type = index_name) and time.time() - t0 < wait_time:
        time.sleep(0.01)
        pass

    time_indexing = time.time()
    upload_file_into_es(file_path = file_path,
                        index_name = index_name,
                        read_chunk_size = read_chunk_size,
                        parallel_jobs_count = parallel_jobs_count,
                        index_chunk_size = index_chunk_size,
                        delimeter = delimeter)
    stop_time = time.time()


    current_file.upload_into_es_settings_rcs = read_chunk_size
    current_file.upload_into_es_settings_pp = parallel_jobs_count
    current_file.upload_into_es_settings_ics = index_chunk_size
    current_file.upload_into_es_ttm = stop_time - time_creation
    current_file.upload_into_es_itm = stop_time - time_indexing
    current_file.upload_into_es_indexing_done = django_now()
    current_file.save()
