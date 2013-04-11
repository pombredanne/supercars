#!/bin/bash

BASE_DIR=`dirname $0`

echo ""
echo "Starting Karma / Testacular Server (http://karma-runner.github.com)"
echo "-------------------------------------------------------------------"

karma start $BASE_DIR/../test/jasmine/karma.conf.js $*
