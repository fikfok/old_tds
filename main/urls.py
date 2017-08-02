from django.conf.urls import url
from main.views import main, task_status, get_data, get_filters


urlpatterns = (
    url(r'^main/$', main.as_view(), name = 'main'),
    url(r'^main/task_status/(?P<task_id>.+)$', task_status, name = 'task_status'),
    url(r'^main/get_data_from_(?P<index_name>.+)_between_(?P<row_from>\d+)_and_(?P<row_to>\d+)$', get_data, name = 'get_data'),
    url(r'^main/get_filters$', get_filters, name = 'get_filters'),
)