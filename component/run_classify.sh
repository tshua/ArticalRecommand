#!/bin/bash

# sh run_classify.sh > ../log/run_classify_log 2>&1 &

while true
do
   echo "----------------------------"
   python3 bayes_sort.py classify
   if [ $? -eq 1 ]
   then
       break
   fi
   sleep 1
done

echo "classify over"