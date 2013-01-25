#!/bin/bash

# (c) Mark Fink, 2008 - 2013
# This script is released under the MIT License
# Warranty in any form is excluded

# Start jmx counters for Java applications

if [ $# -ne 4 ]
then
  echo " Start jmx counters every 5 seconds"
  echo "Usage: `basename $0` HOST HTTPPORT JMXCREDENTIALS NUMBER_OF_SECONDS "
  exit 1
fi

DURATION="$1"
HOST="$2"
HTTPPORT="$3"
CRED="$4"

TURL="http://$HOST:$HTTPPORT/manager/jmxproxy?qry=Catalina:name=http-$HTTPPORT,type=ThreadPool"
CURL="http://$HOST:$HTTPPORT/manager/jmxproxy?qry=com.mchange.v2.c3p0:type=PooledDataSource*"
SURL="http://$HOST:$HTTPPORT/manager/jmxproxy?qry=Catalina:type=Manager,path=/ecom,host=localhost"
START=`TZ=CET date '+%s'`
SUFFIX=`TZ=CET date '+%y%m%d%H'`  
LOGFILE="_app/jmx.txt.${SUFFIX}"

# create _os directory where the app counter logfiles are stored
if [ ! -d "_app" ]; then
    mkdir _app
fi

rm _app/*.pid
touch _app/${SUFFIX}.pid

echo "timestamp;currentThreadCount;maxThreads;numBusyConnections;maxPoolSize;activeSessions" > $LOGFILE

print_metrics () {
    TS=`TZ=CET date +'%Y%m%d %H%M%S'`

    OUTPUT=$(curl --user $CRED $TURL 2>/dev/null)
    TC=$(echo -e $OUTPUT | sed "s/.*currentThreadCount: \([0-9]*\).*/\1/")
    TM=$(echo -e $OUTPUT | sed "s/.*maxThreads: \([0-9]*\).*/\1/")

    OUTPUT=$(curl --user $CRED $CURL 2>/dev/null)
    CC=$(echo -e $OUTPUT | sed "s/.*numBusyConnections: \([0-9]*\).*/\1/")
    CM=$(echo -e $OUTPUT | sed "s/.*maxPoolSize: \([0-9]*\).*/\1/")

    OUTPUT=$(curl --user $CRED $SURL 2>/dev/null)
    SA=$(echo -e $OUTPUT | sed "s/.*activeSessions: \([0-9]*\).*/\1/")

    echo "$TS;$TC;$TM;$CC;$CM;$SA" >> $LOGFILE
}

export -f print_metrics

while [ $(( $(date '+%s') - $DURATION )) -lt $START ]; do
    print_metrics
    sleep 5
done
