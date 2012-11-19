@echo off
REM execute webservice performance test

set JMETER="C:\workspace\physmon-perftest\apache-jmeter-2.6\bin\jmeter.bat"
SET SUFFIX=%date:~8,2%%date:~3,2%%date:~0,2%%time:~0,2%
SET SUFFIX=%SUFFIX: =0%
set DURATION=36000

REM start jmeter
start /wait cmd /C %JMETER% -n -twebservice_scenario/testplan.jmx -lwebservice_scenario/results.txt.%SUFFIX% -jwebservice_scenario/jmeter.log.%SUFFIX% -Jduration=%DURATION%

REM create folder for testresults
mkdir "testruns/%SUFFIX%"

REM collect test results
cd webservice_scenario/
tar -cf "../testruns/%SUFFIX%/jmeter-logs-%SUFFIX%.tar" *.%SUFFIX%
cd ..
gzip -f "testruns/%SUFFIX%/jmeter-logs-%SUFFIX%.tar"
del /q testruns\%SUFFIX%\jmeter-logs-%SUFFIX%.tgz
rename "testruns\%SUFFIX%\jmeter-logs-%SUFFIX%.tar.gz" "jmeter-logs-%SUFFIX%.tgz"
