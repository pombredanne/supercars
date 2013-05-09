#!/bin/bash

BASE_DIR=`dirname $0`

BASEDIR=$( cd $(dirname $0) ; cd .. ; pwd -P )

RUNTIME=$BASEDIR/../tutorial_ci/runtime
KARMA=$RUNTIME/node/bin/karma



echo ""
echo "Starting Karma / Testacular Server (http://karma-runner.github.com)"
echo "-------------------------------------------------------------------"

$KARMA start $BASE_DIR/../test/jasmine/karma.conf.js $*
