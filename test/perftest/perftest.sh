#!/bin/bash

# (c) Mark Fink, 2008 - 2013
# This script is released under the MIT License
# Warranty in any form is excluded

SCRIPTPATH=$( cd $(dirname $0) ; pwd -P )

DURATION=1800

PATH=$PATH:/opt/sun/jdk1.6.0_07/bin
JMETER=$SCRIPTPATH/../../../tutorial_ci/runtime/apache-jmeter-2.9/bin/jmeter.sh
SUFFIX=`TZ=CET date '+%y%m%d%H'`

mkdir _jmeter

# start jmeter
$JMETER -n -tscenarios/testplan.jmx -l_jmeter/results.txt.$SUFFIX \
    -j_jmeter/jmeter.log.$SUFFIX -Jduration=$DURATION -pjmeter.properties

# create folder for testresults
mkdir -p testruns/$SUFFIX

# archive test results
cd _jmeter/
tar -cf ../testruns/$SUFFIX/jmeter-logs-$SUFFIX.tar *.$SUFFIX
cd ..
gzip -f testruns/$SUFFIX/jmeter-logs-$SUFFIX.tar
