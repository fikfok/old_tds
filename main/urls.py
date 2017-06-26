from django.conf.urls import url
from main.views import main, test

urlpatterns = (
    url(r'^main/$', main.as_view(), name = 'main'),
    url(r'^test/$', test.as_view(), name = 'test'),
)