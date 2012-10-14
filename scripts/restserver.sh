#!/bin/bash 

##
# start|stop|restart python restserver
#
# USAGE:
#   ./scripts/manage_restserver.sh start|stop|restart
#
# VIEW:
#   http://localhost:8000

BASE_DIR=`dirname $0`

case $1 in
    "start" )
        echo "start python restserver"
        nohup python $BASE_DIR/../backend/restserver.py > /tmp/nohup.out 2> /tmp/nohup.out &
        ;;
    "stop" )
        echo "stop python restserver"
        kill `ps aux | grep "/backend/restserver.py" | grep -v grep | awk '{print $2}'` > /dev/null
        ;;
    "restart" )
        echo "restart python restserver"
        kill `ps aux | grep "/backend/restserver.py" | grep -v grep | awk '{print $2}'` > /dev/null 
        nohup python $BASE_DIR/../backend/restserver.py > /tmp/nohup.out 2> /tmp/nohup.out &
        ;;
    *)
        echo "need start|stop|restart"
        exit 1
esac