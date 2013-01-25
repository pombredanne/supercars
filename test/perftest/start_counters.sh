#!/bin/bash
# (c) Mark Fink, 2008 - 2013
# This script is released under the MIT License
# Warranty in any form is excluded

echo "run the OS counters for <number of seconds> on remote systems"
python scripts/start_counters.py "Sakai, Uji" "oscounters.sh" "2000"

echo "run the JMX counters for <number of seconds> on remote systems"
python scripts/start_counters.py "Sakai, Uji" "appcounters.sh" "2000" \
    "host" "httpport" "jmxcredentials"

