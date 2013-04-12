#!/bin/bash

# (c) Mark Fink, 2008 - 2013
# This script is released under the MIT License
# Warranty in any form is excluded

TESTRUN="13041118"
START_TIME="2013-04-11 18:30:00"
END_TIME="2013-04-11 19:00:00"

SCRIPTPATH=$( cd $(dirname $0) ; pwd -P )
PYTHON=$SCRIPTPATH/../../../tutorial_ci/runtime/pyrun/bin/pyrun

# remove old plot_error.log if any
#IF EXIST testruns\%testrun%\plot_error.log (
#    del /q testruns\%testrun%\plot_error.log
#)
rm testruns/$TESTRUN/plot_error.log

# create _plots folder
#IF NOT EXIST testruns\%testrun%\_plots (
#    mkdir testruns\%testrun%\_plots
#)
mkdir -p testruns/$TESTRUN/_plots

# collect logfiles
#REM IF EXIST testruns\%testrun%\collect.lock (
#    REM prevent recollection and possible destruction of logfiles
#    REM oscounter logs are removed from server during logfile collection
#    REM jvm-gclogs are cleaned up during server start
#REM     echo Operation aborted! Logfiles have already been collected for testrun %testrun%.
#REM     GOTO:EOF
#REM )
$PYTHON scripts/collect_logs.py "%testrun%" "Laptop" "oscounters"
touch testruns/$TESTRUN/collect.lock

# create plots
# oscounters
$PYTHON scripts/plot.py "$TESTRUN" "$START_TIME" "$END_TIME" "Laptop" \
    "sar, vmstat, top" "testruns/$TESTRUN" "testruns/$TESTRUN/_plots"

# webservice results
$PYTHON scripts/plot_jmeter.py "Laptop" \
    "testruns/$TESTRUN/jmeter-logs-$TESTRUN.tar.gz" \
    testruns/$TESTRUN/_plots \
    scenarios/loadmodel_supercars_quick_v0.1.xls \
    "$START_TIME" "$END_TIME"

# archive all plots
#python scripts/archive_plots.py "$TESTRUN"


# check the plot_error.log file
#for /f %%a in ('type "testruns\%testrun%\plot_error.log"^|find "" /v /c') do set cnt=%%a
#if not %cnt% == 0 (
#    echo #############################################################
#    echo ### ERROR! We discovered %cnt% problems during processing.
#    echo ### Please refer to plot_error.log for details!
#    echo #############################################################
#)


#if [ $# -ne 4 ]
#then
#  echo "Usage: `basename $0` YYMMDDHH hostname 'YYYY-MM-DD HH:MM:SS' 'YYYY-MM-DD #HH:MM:SS'"
#  exit 1
#fi
