from django.views.generic.base import TemplateView
from main.forms import DocumentForm
import uuid
import os
from django.conf import settings
from elasticsearch import Elasticsearch
from main.upload_file_into_es import upload_file_into_es

import time
from django.http import JsonResponse
import pandas as pd


class main(TemplateView):
    template_name = 'main.html'

    res_list = []
    file_type = True
    es_data = {}
    # context = {}
    json_response = {}

    def post(self, request, **kwargs):
        file_name = str(uuid.uuid4())
        context = super(main, self).get_context_data(**kwargs)
        if 'submit-upload-files' in request.POST and request.FILES['file'].name.split('.')[-1] == 'csv':
            form = DocumentForm(request.POST, request.FILES)
            handle_uploaded_file(request.FILES['file'], new_file_name = file_name)
            time.sleep(0.9)
            es_data = {'data': retrieve_es_data(index_name = file_name)}
            context['form'] = form
            context['res_list'] = self.res_list
            context['file_type'] = self.file_type
            context['es_data'] = es_data
            context['file_size'] = request.POST['file_size']
        elif 'submit-upload-files' in request.POST and request.FILES['file'].name.split('.')[-1] != 'csv':
            self.file_type = False
            context['file_type'] = self.file_type
        if self.request.is_ajax():
            self.json_response['response_file_name'] = request.POST['file_name']
            self.json_response['response_file_type'] = request.FILES['file'].name.split('.')[-1]
            self.json_response['response_file_size'] = request.POST['file_size']
            self.json_response['response_es_data'] = es_data
            return JsonResponse(self.json_response)
        return super(main, self).render_to_response(context)


def handle_uploaded_file(f, new_file_name):
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

    put_data_in_es(i_name = new_file_name, d_type = new_file_name, file_path = absolut_path)
    return

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
    es.indices.put_mapping(index = i_name, doc_type = d_type, body = mapping)
    upload_file_into_es(file_path = file_path, index_name = i_name, doc_type = d_type)

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



