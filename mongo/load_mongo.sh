#!/bin/bash

option=0

DB_PATH1="/data/db/ArticleRecommend/RS_A"
DB_PATH2="/data/db/ArticleRecommend/RS_B"
DB_PATH3="/data/db/ArticleRecommend/RS_C"

DB_CONF1="../conf/mongo_rsa.conf"
DB_CONF2="../conf/mongo_rsb.conf"
DB_CONF3="../conf/mongo_rsc.conf"

DB_LOG1="../log/db/rsa_log"
DB_LOG2="../log/db/rsb_log"
DB_LOG3="../log/db/rsc_log"

DB_SETTING="../conf/setting.js"

if [ ! $1 ]
then
	echo "********************************************************"
	echo "args help:"
	echo "init  :  init_mongo_database,it would be used first time."
	echo "start :  start mongo_database."
	echo "stop  :  stop  mongo_database."
	echo "********************************************************"
	exit 0
elif [ $1 = "init" ]
then
	option=1
	echo "init DB selected"
elif [ $1 = "start" ]
then
	option=2
	echo "start DB selected"
elif [ $1 = "stop" ]
then
	ps -ef | grep mongod
	killall mongod
	echo "kill all mongod"
	sleep 1s
	ps -ef | grep mongod
	exit
else
	echo "invalid arg"
	exit 0
fi


if [ -d $DB_PATH1 -a -d $DB_PATH2 -a -d $DB_PATH3 ]
then
	echo "dir exist"
else
	if [ $option -eq 2 ]
	then
		echo "can't start DB,there is no such dirtionary."
		exit 0
	elif [ $option -eq 1 ]
	then
		mkdir -p $DB_PATH1 $DB_PATH2 $DB_PATH3 
		echo "mkdir..."
	fi
fi

nohup mongod --config $DB_CONF1 > $DB_LOG1 2>&1 & 
echo "start RS_A"
nohup mongod --config $DB_CONF2 > $DB_LOG2 2>&1 & 
echo "start RS_B"
nohup mongod --config $DB_CONF3 > $DB_LOG3 2>&1 & 
echo "start RS_C"

if [ $option -eq 1 ]
then
	sleep 1s
	echo "init rs config"	
	mongo 127.0.0.1:27017 $DB_SETTING
fi

echo "done"
