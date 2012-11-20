@echo off
REM execute webservice performance test

set JMETER="apache-jmeter-2.6\bin\jmeter.bat"
SET SUFFIX=%date:~8,2%%date:~3,2%%date:~0,2%%time:~0,2%
SET SUFFIX=%SUFFIX: =0%
REM set SUFFIX=`date '+%y%m%d%H'`
REM set HOST=kyoto
REM set PORT=99
set DURATION=3600

REM start jmeter
%JMETER% -twebservice_scenario/testplan.jmx -lwebservice_scenario/results.txt.%SUFFIX% -jwebservice_scenario/jmeter.log.%SUFFIX% -Jduration=%DURATION%
