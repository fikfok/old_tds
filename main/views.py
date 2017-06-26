from django.views.generic.base import TemplateView
from main.forms import DocumentForm
import uuid
import os
from django.conf import settings
import subprocess
import shlex
from elasticsearch import Elasticsearch
import time
from django.http import JsonResponse

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

    hm = os.environ['HOME'] + '/'
    virtual_env = 'my_env'
    index_name = new_file_name
    doc_type = new_file_name
    command = shlex.split('/bin/bash -c "source ' + hm + virtual_env + '/bin/activate && csv2es --index-name ' + index_name + ' --doc-type ' + doc_type + ' --import-file ' + absolut_path + ' --tab"')
    subprocess.call(command)
    return

def retrieve_es_data(index_name):
    es = Elasticsearch()
    es_search_result = es.search(index = index_name, body = {"query": {"match_all": {}}, "size": 100})
    result = []
    result.append(list(es_search_result['hits']['hits'][0]['_source'].keys()))

    for hit in es_search_result['hits']['hits']:
        result.append(list(hit['_source'].values()))
    return result




class test(TemplateView):
    template_name = 'test.html'
