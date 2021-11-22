#! /bin/bash

passwd root
passwd iree

service mysql start
service ssh start

python manage.py migrate
python manage.py createsuperuser