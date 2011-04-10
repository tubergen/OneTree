#!/bin/sh
echo 'y\n' | mysqladmin -u root -p drop django_database;
mysqladmin -u root -p create django_database;
python manage.py syncdb 
echo python manage.py syncdb