@echo off
REM (c) Mark Fink, 2008 - 2013
REM This script is released under the MIT License
REM Warranty in any form is excluded

REM testrun
set testrun=13012511
set startTime=2013-01-25 11:15:00
set endTime=2013-01-25 11:20:00

REM remove old plot_error.log if any
IF EXIST testruns\%testrun%\plot_error.log (
    del /q testruns\%testrun%\plot_error.log
)

REM create _plots folder
IF NOT EXIST testruns\%testrun%\_plots (
    mkdir testruns\%testrun%\_plots
)

REM Testenvironment Systemtest

REM collect logfiles
REM IF EXIST testruns\%testrun%\collect.lock (
    REM prevent recollection and possible destruction of logfiles
    REM oscounter logs are removed from server during logfile collection
    REM jvm-gclogs are cleaned up during server start
REM     echo Operation aborted! Logfiles have already been collected for testrun %testrun%.
REM     GOTO:EOF
REM )
REM python scripts/collect_logs.py "%testrun%" "Abaiang, Abemama, Tamana" "oscounters, gclogs, applogs"
REM python scripts/collect_logs.py "%testrun%" "Abaiang, Abemama" "traces"
python scripts/collect_logs.py "%testrun%" "Sakai" "oscounters, appcounters"
REM re  echo. 2>testruns\%testrun%\collect.lock

REM create plots
REM python scripts/plot.py "%testrun%" "%startTime%" "%endTime%" "Abaiang, Abemama, Tamana" "gc" ^
REM     "testruns/%testrun%" "testruns/%testrun%/_plots"

REM python scripts/plot.py %testrun% "%startTime%" "%endTime%" "Abaiang, Abemama" "traces" ^
REM     "testruns/%testrun%" "testruns/%testrun%/_plots"
REM python scripts/plot.py "%testrun%" "%startTime%" "%endTime%" "Seeland" "vmstat" "testruns/%testrun%" "testruns/%testrun%/_plots"
python scripts/plot.py "%testrun%" "%startTime%" "%endTime%" "Seeland" "jmx" "testruns/%testrun%" "testruns/%testrun%/_plots"

REM physmon combined 90th percentile
REM python scripts/plot_physmon_p90.py "%testrun%" "%startTime%" "%endTime%" "Abaiang, Abemama" "testruns/%testrun%" "testruns/%testrun%/_plots"


REM webservice results
REM python scripts/plot_jmeter.py Abaiang-Abemama "testruns/%testrun%/jmeter-logs-%testrun%.tgz" testruns/%testrun%/_plots ^
REM    C:\workspace\physmon-perftest\webservice_scenario\20120417_Performancetest_Model_physmon_average_v0.1.xls ^
    "%startTime%" "%endTime%"


REM debug single plot script
REM python scripts/plot_physmon.py "Abaiang" "testruns/%testrun%/Abaiang-traces-%testrun%.tgz" "testruns/%testrun%/_plots" "%startTime%" "%endTime%" 
REM python scripts/plot_physmon.py "Abemama" "testruns/%testrun%/Abemama-traces-%testrun%.tgz" "testruns/%testrun%/_plots" "%startTime%" "%endTime%" 


REM archive all plots
REM python scripts/archive_plots.py "%testrun%"


REM check the plot_error.log file
for /f %%a in ('type "testruns\%testrun%\plot_error.log"^|find "" /v /c') do set cnt=%%a
if not %cnt% == 0 (
    echo #############################################################
    echo ### ERROR! We discovered %cnt% problems during processing.
    echo ### Please refer to plot_error.log for details!
    echo #############################################################
)