#!/bin/bash

in_file="$1"
db_name="cellcomm"
coll_name="cells"

if [[ ! -f ${in_file} ]]; then
  echo "no cell-data file found: $in_file"
  exit -1
fi

IFS=
read -p "Overwrite cell-data with \"${in_file}\" [Y/n] " -s -n 1 answer
echo
if [[ ${answer} =~ ^[Yy]$ ]] || [[ ${answer} = "" ]]; then
  mongoimport --drop --jsonArray --db=${db_name} --collection=${coll_name} --file=${in_file}
fi
