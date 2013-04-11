#!/bin/bash
#
# Stops all req. server processes, FitNesse, Jenkins
# 

# Ajaxdemo
~/devel/ajaxdemo/scripts/restserver.sh stop

# FitNesse
~/devel/ajaxdemo/scripts/fitnesse_srv.sh stop

# Jenkins
echo "stop jenkins server"
kill `ps aux | grep "jenkins" | grep -v grep | awk '{print $2}'` > /dev/null

# Slides
echo "stop presentation server"
kill `ps aux | grep "SimpleHTTPServer" | grep -v grep | awk '{print $2}'` > /dev/null
