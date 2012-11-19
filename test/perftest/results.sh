#!/bin/bash

# create plots for performance test execution

if [ $# -ne 4 ]
then
  echo "Usage: `basename $0` YYMMDDHH hostname 'YYYY-MM-DD HH:MM:SS' 'YYYY-MM-DD HH:MM:SS'"
  exit 1
fi
APPLOGS="testruns/$1/app_logs_$1.tar.gz"
PYTHON="../../env/bin/python"
JMETERLOGS="testruns/$1/jmeter_logs_$1.tar.gz"
PLTFOLDER=_plots/
LOADMODEL=./20111216_Performancetest_Model_boodo_average_v0.1.xls

mkdir $PLTFOLDER

#$PYTHON scripts/plot_vmstat.py $2 $APPLOGS $PLTFOLDER "$3" "$4"
#$PYTHON scripts/plot_sar.py    $2 $APPLOGS $PLTFOLDER "$3" "$4"
#$PYTHON scripts/plot_top.py    $2 $APPLOGS $PLTFOLDER "$3" "$4"
#$PYTHON scripts/plot_access.py $2 $APPLOGS $PLTFOLDER "$3" "$4"
#$PYTHON scripts/plot_jmeter.py $2 $JMETERLOGS $PLTFOLDER $LOADMODEL "$3" "$4"
$PYTHON scripts/plot_physmon.py $2 $TRACELOGS $PLTFOLDER "$3" "$4"

# put all the plots into an archive
cd _plots/
tar -cf ../testruns/$1/plots_$1.tar *.png *.html
cd ..
tar -rf testruns/$1/plots_$1.tar plot_error.log
gzip -f testruns/$1/plots_$1.tar

# clean up
rm -rf $PLTFOLDER
rm plot_error.log

