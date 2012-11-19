#!/bin/bash

# (c) Mark Fink, 2008 - 2012
# This script is released under the Modified BSD License
# Warranty in any form is excluded

# Start counters for linux environment
# * vmstat every 5 seconds
# * top every 30 seconds
# * sar every 5 seconds

if [ $# -ne 1 ]
then
  echo " Start counters vmstat every 5 seconds, top every 30 seconds and sar every 5 seconds"
  echo "Usage: `basename $0` NUMBER_OF_SECONDS"
  exit 1
fi

# create _os directory where the os counter logfiles are stored
if [ ! -d "_os" ]; then
    mkdir _os
fi

# wait till full minute
sleep $[60-`date +'%S'`]

SECONDS=$1
let FIVESEC=$SECONDS/5
let THRTHYSEC=$SECONDS/30
# handle datetime info in local time
HEADER_5s=`TZ=CET date +'%Y%m%d %H%M%S interval 5 sec'`
HEADER_30s=`TZ=CET date +'%Y%m%d %H%M%S interval 30 sec'`
SUFFIX=`TZ=CET date '+%y%m%d%H'`  

#echo " $SECONDS $FIVESEC $THRTHYSEC $SUFFIX"
echo $HEADER_5s > _os/vmstat.txt.$SUFFIX; vmstat 5 $FIVESEC >> _os/vmstat.txt.$SUFFIX &
printf "$!\n" > _os/${SUFFIX}.pid
echo $HEADER_30s > _os/top.txt.$SUFFIX; TZ=CET top -bd 30 -n $THRTHYSEC >> _os/top.txt.$SUFFIX &
printf "$!\n" >> _os/${SUFFIX}.pid
#echo $HEADER_5s > _os/sar.txt.$SUFFIX; sar -n DEV,EDEV 5 $FIVESEC >> _os/sar.txt.$SUFFIX &
echo $HEADER_5s > _os/sar.txt.$SUFFIX; TZ=CET sar -n DEV -n EDEV 5 $FIVESEC >> _os/sar.txt.$SUFFIX &
printf "$!\n" >> _os/${SUFFIX}.pid

#  TZ=CET S_TIME_FORMAT=ISO
#  S_TIME_DEF_TIME

echo 'Started counters to run for ' $1 ' seconds.'

