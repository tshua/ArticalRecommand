#!/bin/bash

# sh run_train.sh > ../log/run_train_log 2>&1 &

while true
do
   echo "----------------------------"
   python3 bayes_sort.py train
   if [ $? -eq 1 ]
   then
        break
   fi
   sleep 1
done

echo "train over"