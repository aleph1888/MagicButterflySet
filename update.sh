#!/bin/bash

#This script needs to be executed on the local directory of the repository
#update from the git repo
#git pull

user='gestioCI'
password='gestioCI'
dbName='gestioCI_butterfly'
host='localhost'

echo "dropping all tables"

for i in `mysql -u$user -p$password -h $host  $dbName -e "show tables" | grep -v Tables_in` ; do mysql -u$user -p$password -h $host $dbName -e "SET FOREIGN_KEY_CHECKS = 0; drop table $i ; SET FOREIGN_KEY_CHECKS = 1" ; done

echo "sync database"
cp Config/settings1.py Config/settings.py 
python manage.py syncdb

echo "migrating General"

python manage.py makemigrations General
python manage.py migrate General

echo "migrating Welcome"

cp Config/settings2.py Config/settings.py
python manage.py makemigrations Welcome
python manage.py migrate Welcome

echo "update database"

mysql -u $user -p$password -h $host $dbName < basic_data.sql
mysql -u $user -p$password -h $host $dbName < bdgestiociProduccio.sql

echo "migrating public_form"

cp Config/settings3.py Config/settings.py
python manage.py makemigrations public_form
python manage.py migrate public_form

echo "end of the script"
