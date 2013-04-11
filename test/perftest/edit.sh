#!/bin/bash

SCRIPTPATH=$( cd $(dirname $0) ; pwd -P )

JMETER=~/devel/tutorial_ci/runtime/apache-jmeter-2.9/bin/jmeter.sh
SUFFIX=`TZ=CET date '+%y%m%d%H'`
HOST=boodo-site
PORT=99
DURATION=36000

# start jmeter in GUI mode
$JMETER -tscenarios/testplan.jmx -l_jmeter/results.txt.$SUFFIX \
    -j_jmeter/jmeter.log.$SUFFIX -Jduration=$DURATION \
    -Jhost=$HOST -Jport=$PORT
