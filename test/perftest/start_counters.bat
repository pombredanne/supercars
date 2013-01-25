@echo off
REM (c) Mark Fink, 2008 - 2013
REM This script is released under the MIT License
REM Warranty in any form is excluded

REM "run the OS counters for <number of seconds> on remote systems"
python scripts/start_counters.py "Sakai" "oscounters.sh" "2000"

REM "run the JMX counters for <number of seconds> on remote systems"
python scripts/start_counters.py "Sakai, Uji" "appcounters.sh" "40000" ^
    "host" "httpport" "jmxcredentials"
