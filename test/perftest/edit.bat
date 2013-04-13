@echo off
REM execute webservice performance test

set JMETER="%cd%\..\..\..\tutorial_ci\runtime\apache-jmeter-2.9\bin\jmeter.bat"
SET SUFFIX=%date:~8,2%%date:~3,2%%date:~0,2%%time:~0,2%
SET SUFFIX=%SUFFIX: =0%
REM set SUFFIX=`date '+%y%m%d%H'`
REM set HOST=kyoto
REM set PORT=99
set DURATION=3600

REM start jmeter
%JMETER% -tscenarios/testplan.jmx -l_jmeter/results.txt.%SUFFIX% -j_jmeter/jmeter.log.%SUFFIX% -Jduration=%DURATION%
