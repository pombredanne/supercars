#!/bin/bash 

##
# start|stop|restart selenium server
#
# USAGE:
#   ./scripts/selenium_srv.sh start|stop|restart
#

SELENIUM_CMD='java -jar ./test/fitnesse/lib/selenium-server-standalone*.jar -multiwindow -port 4444'

case $1 in
    "start" )
        echo "start selenium server"
        nohup $SELENIUM_CMD > /tmp/nohup.out 2> /tmp/nohup.out &
        ;;
    "stop" )
        echo "stop selenium server"
        kill `ps aux | grep "java -jar ./test/fitnesse/lib/selenium-server-standalone" | grep -v grep | awk '{print $2}'` > /dev/null
        ;;
    "restart" )
        echo "restart selenium server"
        kill `ps aux | grep "java -jar ./test/fitnesse/lib/selenium-server-standalone" | grep -v grep | awk '{print $2}'` > /dev/null 
        nohup $SELENIUM_CMD > /tmp/nohup.out 2> /tmp/nohup.out &
        ;;
    *)
        echo "need start|stop|restart"
        exit 1
esac

