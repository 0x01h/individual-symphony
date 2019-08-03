#!/usr/bin/bash

python3 manage.py inspectdb > individualsymphony/models.py
python3 manage.py makemigrations
python3 manage.py migrate