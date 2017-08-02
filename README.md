# Prerequisites

- install Django > 1.10.6
- install python > 3.5 and configure virtualenv
- pip install elasticsearch
- Install Miniconda (https://conda.io/docs/install/quick.html)
- conda install pandas
- conda install joblib

Tools for periodic tasks:
[RabbitMQ](http://www.deenter.com/2016/01/25/how-to-install-celery-on-django-and-create-a-periodic-task/)

- sudo apt-get install rabbitmq
- sudo rabbitmq-server -detached
- sudo rabbitmqctl add_user admin admin
                            ^login ^password
- sudo rabbitmqctl add_host myvhost
- sudo rabbitmqctl set_permissions -p myvhost admin ".*" ".*" ".*"

Celery (http://www.lexev.org/2014/django-celery-setup/):
- pip install celery==3.1.25
                      ^strongly (problem with 4.0: https://stackoverflow.com/questions/40540769/importerror-no-module-named-timeutils)
- pip install django-celery

Run celery and worker:
- python manage.py celery worker -B --concurrency=1

