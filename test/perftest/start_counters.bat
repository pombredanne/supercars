@echo off

REM (c) Mark Fink, 2008 - 2013
REM This script is released under the MIT License
REM Warranty in any form is excluded

set SCRIPTPATH=%cd%
set PYTHON=%SCRIPTPATH%\..\..\..\tutorial_ci\runtime\python\python

REM "IMPORTANT: Use this script to start OS counters on a remote Unix host"
REM "You can NOT use this script to start OS counters on a Windows machine"
REM "You must use Perfmon to collect OS counters on Windows"

REM "run the OS counters for <number of seconds> on remote systems"
%PYTHON% scripts/start_counters.py "VM-UBUNTU" "oscounters.sh" "2000"

REM "run the JMX counters for <number of seconds> on remote systems"
REM python scripts/start_counters.py "Laptop" "appcounters.sh" "2000" ^
REM     "host" "httpport" "jmxcredentials"
