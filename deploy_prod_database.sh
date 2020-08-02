#!/usr/bin/env bash

if [[ -z ${1} ]]; then
  echo -e "required parameter: deploy_prod_database.sh <tunnel-port>"
  echo -e "\nlocal tunnel example: ssh -L <tunnel-port>:localhost:27017 <user>@<host>"
  exit -1
fi

SSH_PORT="$1"
DB_NAME="cellcomm-stage"

mongodump --db="${DB_NAME}" --collection="encs" --archive | mongorestore --port=${SSH_PORT} --archive
mongodump --db="${DB_NAME}" --collection="encits" --archive | mongorestore --port=${SSH_PORT} --archive
mongodump --db="${DB_NAME}" --collection="genes" --archive | mongorestore --port=${SSH_PORT} --archive

