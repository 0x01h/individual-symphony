#!/usr/bin/bash

redis-cli flushall
redis-cli flushdb
python3 manage.py createcachetable
django-admin.py makemessages -l tr --ignore=tools/* --ignore=manage.py --ignore=website/*
django-admin.py compilemessages
python3 manage.py collectstatic
python3 manage.py runserver
