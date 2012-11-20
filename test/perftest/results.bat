@echo off
REM testrun
set testrun=12042508
set startTime=2012-04-25 08:00:00
set endTime=2012-04-25 11:00:00

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
REM python scripts/collect_logs.py "%testrun%" "Sakai, Uji" "oscounters, gclogs, applogs"
REM python scripts/collect_logs.py "%testrun%" "Sakai, Uji" "traces"
REM re  echo. 2>testruns\%testrun%\collect.lock

REM create plots
REM python scripts/plot.py "%testrun%" "%startTime%" "%endTime%" "Sakai, Uji" "gc" ^
REM     "testruns/%testrun%" "testruns/%testrun%/_plots"



REM webservice results
REM python scripts/plot_jmeter.py Abaiang-Abemama "testruns/%testrun%/jmeter-logs-%testrun%.tgz" testruns/%testrun%/_plots ^
REM     webservice_scenario\20120417_Performancetest_Model_average_v0.1.xls ^
REM     "%startTime%" "%endTime%"


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