#!/bin/bash

SCRIPTPATH=$( cd $(dirname $0) ; pwd -P )

PATH=$PATH:/opt/sun/jdk1.6.0_07/bin
JMETER=~/devel/tutorial_ci/runtime/apache-jmeter-2.8/bin/jmeter.sh
SUFFIX=`TZ=CET date '+%y%m%d%H'`
DURATION=1800

mkdir _jmeter

# start jmeter
$JMETER -n -twebservice_scenario/testplan.jmx -l_jmeter/results.txt.$SUFFIX \
    -j_jmeter/jmeter.log.$SUFFIX -Jduration=$DURATION 

# create folder for testresults
mkdir testruns/$SUFFIX

# archive test results
cd _jmeter/
tar -cf ../testruns/$SUFFIX/jmeter-logs-$SUFFIX.tar *.$SUFFIX
cd ..
gzip -f testruns/$SUFFIX/jmeter-logs-$SUFFIX.tar
