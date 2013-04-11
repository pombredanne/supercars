#!/bin/bash

# (c) Mark Fink, 2008 - 2013
# This script is released under the MIT License
# Warranty in any form is excluded

SCRIPTPATH=$( cd $(dirname $0) ; pwd -P )
PYTHON=$SCRIPTPATH/../../../tutorial_ci/runtime/pyrun/bin/pyrun

echo "run the OS counters for <number of seconds> on remote systems"
$PYTHON scripts/start_counters.py "Laptop" "oscounters.sh" "300"

#echo "run the JMX counters for <number of seconds> on remote systems"
#python scripts/start_counters.py "Sakai" "appcounters.sh" "2000" \
#    "host" "httpport" "jmxcredentials"

