#!/bin/bash
#
# Starts all req. server processes, FitNesse, Jenkins and browser
# 

# Mac / Linux
if [ $(uname -s) == "Darwin" ]
then
  open=open
else
  open=xdg-open
fi

# Ajaxdemo
~/devel/ajaxdemo/scripts/restserver.sh start
$open http://localhost:8000/

# FitNesse
~/devel/ajaxdemo/scripts/fitnesse_srv.sh start
$open http://localhost:10200/

# Jenkins
~/devel/tutorial_ci/scripts/jenkins.sh&
$open http://localhost:8080/

# Testacular watcher
gnome-terminal -e ~/devel/ajaxdemo/scripts/test.sh

# Slides
cd ~/devel/book/tutorial_slides
./serve.sh 8082&
