@echo off
REM execute performance test

set DURATION=1800

set JMETER="apache-jmeter-2.6\bin\jmeter.bat"
SET SUFFIX=%date:~8,2%%date:~3,2%%date:~0,2%%time:~0,2%
SET SUFFIX=%SUFFIX: =0%

REM start jmeter
start /wait cmd /C %JMETER% -n -tscenarios/testplan.jmx -lscenarios/results.txt.%SUFFIX% -j_jmeter/jmeter.log.%SUFFIX% -Jduration=%DURATION% -pjmeter.properties

REM create folder for testresults
mkdir "testruns/%SUFFIX%"

REM collect test results
cd scenarios/
tar -cf "../testruns/%SUFFIX%/jmeter-logs-%SUFFIX%.tar" *.%SUFFIX%
cd ..
gzip -f "testruns/%SUFFIX%/jmeter-logs-%SUFFIX%.tar"
del /q testruns\%SUFFIX%\jmeter-logs-%SUFFIX%.tgz
rename "testruns\%SUFFIX%\jmeter-logs-%SUFFIX%.tar.gz" "jmeter-logs-%SUFFIX%.tgz"
