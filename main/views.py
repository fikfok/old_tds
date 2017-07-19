from django.views.generic.base import TemplateView
from main.forms import DocumentForm
import os
from django.conf import settings
from elasticsearch import Elasticsearch
from main.upload_file_into_es import upload_file_into_es
from main.models import UploadedFiles
from datetime import datetime
from django.utils.timezone import now as django_now
from django.http import JsonResponse
import pandas as pd
import main.tasks as tasks
from celery.result import AsyncResult

def task_status(request, task_id):
    json_response = {}
    json_response['task_status'] = AsyncResult(task_id).status

    es = Elasticsearch()

    query_search = \
        {
            "size": 0,
            "aggs": {
                "aggs": {
                    "top_hits": {
                        "size": 1,
                        "_source": {
                            "includes": ["col", "row"]
                        },
                        "sort": [
                            {
                                "row": {
                                    "order": "desc"
                                },
                                "col": {
                                    "order": "desc"
                                }
                            }
                        ]
                    }
                }
            }
        }

    current_file = UploadedFiles.objects.get(upload_into_es_task_id = task_id)
    count_docs = es.search(index = current_file.unique_file_name,
                           doc_type = current_file.unique_file_name,
                           body = query_search)
    try:
        rows_count = count_docs['aggregations']['aggs']['hits']['hits'][0]['_source']['row'] + 1
        cols_count = count_docs['aggregations']['aggs']['hits']['hits'][0]['_source']['col'] + 1
        json_response['indexing_status'] = ((rows_count - 1) * current_file.upload_into_es_cols_count + cols_count) / (current_file.upload_into_es_rows_count * current_file.upload_into_es_cols_count) * 100
    except IndexError:
        json_response['indexing_status'] = -1
    return JsonResponse(json_response)


class main(TemplateView):
    template_name = 'main.html'

    res_list = []
    file_type = True
    es_data = {}
    json_response = {}

    def post(self, request, **kwargs):
        file_name = 'tds-' + str(datetime.now()).replace(' ', '-').replace(':', '-').replace('.', '-')
        context = super(main, self).get_context_data(**kwargs)
        if 'submit-upload-files' in request.POST and request.FILES['file'].name.split('.')[-1] == 'csv':
            delimeter = '\t'
            form = DocumentForm(request.POST, request.FILES)
            absolut_file_path, num_rows, num_cols = uploaded_file(request.FILES['file'], new_file_name = file_name, delimeter = delimeter)
            context['form'] = form
            context['res_list'] = self.res_list
            context['file_type'] = self.file_type
            context['file_size'] = request.POST['file_size']

            user_file = UploadedFiles(unique_file_name = file_name,
                                      absolut_file_path = absolut_file_path,
                                      original_file_name = request.FILES['file'].name,
                                      upload_into_es_file_size = request.POST['file_size'],
                                      upload_into_es_rows_count = num_rows,
                                      upload_into_es_cols_count = num_cols,
                                      file_upload_date_time = django_now())
            user_file.save()

            put_file_into_es = tasks.put_data_in_es.delay(index_name = file_name,
                                                           file_path = absolut_file_path,
                                                           read_chunk_size = 50000,
                                                           parallel_jobs_count = 12,
                                                           index_chunk_size = 50000,
                                                           delimeter = delimeter)

            self.json_response['task_id'] = put_file_into_es.task_id

            user_file.upload_into_es_task_id = put_file_into_es.task_id
            user_file.save()

        elif 'submit-upload-files' in request.POST and request.FILES['file'].name.split('.')[-1] != 'csv':
            self.file_type = False
            context['file_type'] = self.file_type
        return JsonResponse(self.json_response)


def uploaded_file(f, new_file_name, delimeter):
    path = settings.MEDIA_ROOT + '/'

    ext = os.path.splitext(f.name)[-1].lower()
    absolut_path = path + new_file_name + ext
    res_list = []
    destination = open(absolut_path, 'wb+')
    for chunk in f.chunks():
        destination.write(chunk)
    destination.close()

    with open(absolut_path) as fl:
        for line in fl:
            res_list.append(line)

    # put_data_in_es(i_name = new_file_name, d_type = new_file_name, file_path = absolut_path)

    num_rows = 0
    num_cols = 0
    if ext[1:] == 'csv':
        with open(absolut_path) as fl:
            num_cols = len(fl.readline().split(delimeter))
            num_rows = sum(1 for line in fl) + 1

    return absolut_path, num_rows, num_cols

def put_data_in_es(i_name, d_type, file_path):
    es = Elasticsearch()
    mapping = \
        {
            "properties": {
                "row": {"type": "long"},
                "col": {"type": "long"},
                "orig_value": {"type": "text", "fields": {"raw_value": {"type": "keyword"}}}
            }
        }
    es.indices.create(index = i_name)
    es.indices.put_mapping(index = i_name, doc_type = i_name, body = mapping)
    upload_file_into_es(file_path = file_path, index_name = i_name)

def retrieve_es_data(index_name):
    es = Elasticsearch()

    query_count_columns = \
        {
            "size": 0,
            "aggs": {
                "columns_count": {
                    "filter": {"term": {"row": 0}},
                    "aggs": {
                        "count": {"value_count": {"field": "col"}}
                    }
                }
            }
        }
    es_search_result = es.search(index = index_name,
                                 doc_type = index_name, body = query_count_columns)
    columns_count = int(es_search_result['aggregations']['columns_count']['doc_count'])
    rows_to_select = 100
    query_size = rows_to_select * columns_count
    query_select_top_N = \
                    {
                        "size": str(query_size),
                        "query": {
                            "range": {
                                "row": {"lt": str(rows_to_select)}
                            }
                        }
                    }

    es_search_result = es.search(
                                index = index_name,
                                doc_type = index_name,
                                body = query_select_top_N,
                                filter_path = ['hits.hits._source'])
    df = pd.DataFrame()

    for item in es_search_result['hits']['hits']:
        df.loc[item['_source']['row'], item['_source']['col']] = item['_source']['orig_value']
    return df.sort_index(axis = 0).sort_index(axis = 1).values.tolist()



