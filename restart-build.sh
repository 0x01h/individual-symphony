#!/usr/bin/bash

redis-cli flushall
redis-cli flushdb
systemctl daemon-reload
python3 manage.py createcachetable
python3 manage.py collectstatic
django-admin.py makemessages -l tr --ignore=tools/* --ignore=manage.py --ignore=website/*
django-admin.py compilemessages
service gunicorn restart
service nginx restart
