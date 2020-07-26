#!/usr/bin/env bash

if [[ -z ${1} ]]; then
  echo -e "required parameter: deploy_prod_database.sh <tunnel-port>"
  echo -e "example: ssh -L 9999:localhost:27017 <user>@<host>"
  exit -1
fi

SSH_PORT="$1"
DB_NAME="cellcomm"
DB_COLLS=(
"cells"
"encs"
)

for coll in ${DB_COLLS[@]}; do
  mongodump --db "${DB_NAME}" --collection "${coll}" --archive | mongorestore --port=${SSH_PORT} --archive
done