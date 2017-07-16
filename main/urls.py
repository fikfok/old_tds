from django.conf.urls import url
from main.views import main, task_status


urlpatterns = (
    url(r'^main/$', main.as_view(), name = 'main'),
    url(r'^main/task_status/(?P<task_id>.+)$', task_status, name = 'task_status'),
)