from django.views.generic.base import TemplateView
from main.forms import DocumentForm
import os
from django.conf import settings
from elasticsearch import Elasticsearch
from main.models import UploadedFiles
from datetime import datetime
from django.utils.timezone import now as django_now
from django.http import JsonResponse
import pandas as pd
import main.tasks as tasks
from celery.result import AsyncResult
import json
import re

def get_filters(request):
    if request.POST:
        raw_output_columns = json.loads(request.POST['output_columns'])
        raw_filters = json.loads(request.POST['filters'])
        output_columns = [{'col': int(item['id'].replace('col_num_', '')), 'alias': item['value']} for item in raw_output_columns['rules']]
        # filters = [{'col': re.search('col_num_(\d{1,})', item['id']).group(1), 'operator': item['operator'], 'val': item['value']} for item in raw_filters['rules']]
        print(raw_output_columns)
        query = str(raw_filters).replace("'", '"')
        for remove_substr in re.findall(r'_filter_num_\d+', query):
            print(remove_substr)
            query.replace(remove_substr, '')
        print(query)

    json_response = {}
    json_response['status'] = 'ok'
    return JsonResponse(json_response)


def task_status(request, task_id):
    json_response = {}
    json_response['task_status'] = AsyncResult(task_id).status

    es = Elasticsearch()

    query_search = \
        {
            "size": 0,
            "aggs": {
                "max_row_num": {"max": {"field": "row_num"}}
            }
        }

    current_file = UploadedFiles.objects.get(upload_into_es_task_id = task_id)
    count_docs = es.search(index = current_file.unique_file_name,
                           doc_type = current_file.unique_file_name,
                           body = query_search)
    try:
        rows_count = count_docs['aggregations']['max_row_num']['value'] + 1
        json_response['indexing_status'] = rows_count / current_file.upload_into_es_rows_count * 100
    except:
        json_response['indexing_status'] = -1
    return JsonResponse(json_response)

def get_data(request, index_name, row_from, row_to):
    json_response = {}
    es = Elasticsearch()

    query_select_top_N = \
                    {
                        "query": {
                            "range": {
                                "row_num": {
                                    "gte": row_from,
                                    "lte": row_to
                                }
                            }
                        },
                        "sort": [
                            {
                              "row_num": {
                                "order": "asc"
                              }
                            }
                        ]
                    }

    es_search_result = es.search(
                                index = index_name,
                                doc_type = index_name,
                                body = query_select_top_N,
                                filter_path = ['hits.hits._source'])
    columns_list = list(set(es_search_result['hits']['hits'][0]['_source'].keys()) - set(['row_num']))
    columns_list.sort(key = lambda x: int(str(x).replace('col_', '')))

    df = pd.DataFrame(columns = columns_list)

    for item in es_search_result['hits']['hits']:
        df.loc[item['_source']['row_num']] = dict({key: item['_source'][key] for key in columns_list})

    json_response['response_es_data'] = df.values.tolist()
        # .sort_index(axis = 0).sort_index(axis = 1).values.tolist()
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
            self.json_response['index_name'] = file_name

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

    num_rows = 0
    num_cols = 0
    if ext[1:] == 'csv':
        with open(absolut_path) as fl:
            num_cols = len(fl.readline().split(delimeter))
            num_rows = sum(1 for line in fl) + 1

    return absolut_path, num_rows, num_cols
