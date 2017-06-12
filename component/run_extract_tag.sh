#!/bin/bash

# sh run_extract_tag.sh > ../log/run_extract_tag_log 2>&1 &

while true
do
   echo "----------------------------"
   python3 extract_tag.py
   if [ $? -eq 1 ]
   then
       break
   fi
   sleep 1
done

echo "extract_tag over"