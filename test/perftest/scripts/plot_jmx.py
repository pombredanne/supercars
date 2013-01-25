#!/usr/bin/env python
"""
For performance testing you need a clear picture about the utilization
of the machine your application is running on.

This script helps you to analyse jmx logs in order to extract information
about machine utilization.

Before you can start the analysing your log files you need to retrieve the jmx
logs from your system.

Before executing the script you need to configure start and end time of your test
and the path of the top logs. Feel free to use this script as a basis for your work.

(c) Mark Fink, 2008 - 2013
This script is released under the MIT License
Warranty in any form is excluded
"""

import logging
import sqlite3
from datetime import datetime
import pytz
from pylab import *

import re
import os
import tarfile


def extract_filenumber(filename):
    """this helper function sorts the log files into the correct order"""
    n = filename.split('.')[-1]
    if n.isalpha():
        return 0
    else:
        return int(n)


def report_threadpool(starttime, endtime, data, reportfile, reporttitle):
    """Create the report file, this part is application specific."""
    # Note: I use Pylab, Pylab is a procedural interface to the
    # matplotlib object-oriented plotting library. Of cause if you
    # prefere the original matplotlib style or any other plotting tool
    # you can use it here
    fig = figure()

    title(reporttitle)

    tz = pytz.timezone('Europe/Berlin').localize(datetime.datetime.now()).strftime('%z')
    xlabel('reported time: %s to %s [UTC %s]' % (starttime, endtime, tz),
        fontsize='small', x=1.0, ha='right')
    ylabel('Blocks/s')

    ts, tc, tm = zip(*data)  # unpack
    # use HTML color names like:
    # http://www.html-color-names.com/color-chart.php
    plot(ts, tm, 'Blue', label='maxThreads')
    plot(ts, tc, 'Lime', label='currentThreadCount')

    axis([None, None, 0, None])
    legend(loc=0)  # 0 for optimized legend placement
    fig.autofmt_xdate()

    savefig(reportfile)

    # cleanup
    clf()
    cla()


def report_connectionpool(starttime, endtime, data, reportfile, reporttitle):
    """Create the report file, this part is application specific."""
    # Note: I use Pylab, Pylab is a procedural interface to the
    # matplotlib object-oriented plotting library. Of cause if you
    # prefere the original matplotlib style or any other plotting tool
    # you can use it here
    fig = figure()

    title(reporttitle)

    tz = pytz.timezone('Europe/Berlin').localize(datetime.datetime.now()).strftime('%z')
    xlabel('reported time: %s to %s [UTC %s]' % (starttime, endtime, tz),
        fontsize='small', x=1.0, ha='right')
    ylabel('Blocks/s')

    ts, cc, cm = zip(*data)  # unpack
    # use HTML color names like:
    # http://www.html-color-names.com/color-chart.php
    plot(ts, cm, 'Blue', label='maxPoolSize')
    plot(ts, cc, 'Lime', label='numBusyConnections')

    axis([None, None, 0, None])
    legend(loc=0)  # 0 for optimized legend placement
    fig.autofmt_xdate()

    savefig(reportfile)

    # cleanup
    clf()
    cla()


def report_sessions(starttime, endtime, data, reportfile, reporttitle):
    """Create the report file, this part is application specific."""
    # Note: I use Pylab, Pylab is a procedural interface to the
    # matplotlib object-oriented plotting library. Of cause if you
    # prefere the original matplotlib style or any other plotting tool
    # you can use it here
    fig = figure()

    title(reporttitle)

    tz = pytz.timezone('Europe/Berlin').localize(datetime.datetime.now()).strftime('%z')
    xlabel('reported time: %s to %s [UTC %s]' % (starttime, endtime, tz),
        fontsize='small', x=1.0, ha='right')
    ylabel('Blocks/s')

    ts, sc = zip(*data)  # unpack
    # use HTML color names like:
    # http://www.html-color-names.com/color-chart.php
    plot(ts, sc, 'Lime', label='activeSessions')

    axis([None, None, 0, None])
    legend(loc=0)  # 0 for optimized legend placement
    fig.autofmt_xdate()

    savefig(reportfile)

    # cleanup
    clf()
    cla()


######################################################################
# It would be possible to store the non application specific parts of
# the script like parse_lines and LogParser in a central file.
# I currently prefer a version that has every thing on board.

def parse_lines(logParsers, fileinp):
    """parse lines from the fileinput and send them to the logparser"""
    while 1:
        line = fileinp.readline()
        #print line
        if not line:
            break
        elif not line.rstrip():
            continue  # skip newlines

        for lp in logParsers:
            if lp.foundEntry(line):
                break
        else:
            # error: none of the logparsers worked on the line
            logger = logging.getLogger('logparser')
            logger.warning(
                #'Could not parse line %s, in file %s >>>%s<<<',
                #fileinp.lineno(), fileinp.filename(), line.rstrip())
                'Could not parse line >>>%s<<<', line.rstrip())


class LogParser(object):
    """holds a reference to the database and the regular expression"""
    def __init__(self, reLine=r'''...''', db=None, callbacks={},
        tablename='logentries'):
        self.callbacks = callbacks
        self.reLine = re.compile(reLine)
        self.tablename = tablename

        self.db = db
        if db:
            # initialize database
            c = self.db.cursor()
            # note that the database field names are extracted from the
            # regular expression
            c.execute('create table ' + tablename + '(' +
                ', '.join(self.reLine.groupindex.keys() +
                self.callbacks.keys()) + ')')
            c.close()

    def foundEntry(self, line):
        """parse on line an put the results into the database"""
        #print 'entry: ' + line
        match = self.reLine.match(line)
        if match:
            #print match.groupdict()
            values = match.groupdict()
            cb_values = [self.callbacks[x](**values) for x in self.callbacks]
            if self.db:
                # insert values into the database
                c = self.db.cursor()
                c.execute('insert into ' + self.tablename + '(' +
                    ', '.join(values.keys() + self.callbacks.keys()) +
                    ') values (' + ', '.join(['?']*(len(values) +
                    len(self.callbacks))) + ')',
                    [] + values.values() + cb_values)
                c.close()
            return True
        else:
            return False  # line did not match, continue with next lp
######################################################################


def main(config):
    """
    The main part contains the configuration that fits your
    analysis situation this is by nature application specific. In
    other words adjust everything in here so it fits your needs!
    """
    # parse the data from the logfiles
    #timestamp;currentThreadCount;maxThreads;numBusyConnections;maxPoolSize;activeSessions
    #20130125 111236;2;200;7;10;747
    #20130125 111241;2;200;8;10;749
    #20130125 111246;2;200;8;10;751
    #20130125 111251;2;200;8;10;753
    #20130125 111256;2;200;7;10;755
    #20130125 111301;2;200;6;10;757

    def timestamp(**kw_args):
        ts = datetime.datetime.strptime(kw_args['ts'], '%Y%m%d %H%M%S')
        return ts

    # central result database which is held in memory
    db = sqlite3.connect(':memory:',
        detect_types=sqlite3.PARSE_COLNAMES)

    callbacks = {'timestamp': timestamp}

    # parse the data from the logfiles
    jmx = LogParser('^(?P<ts>\d{8} \d{6});(?P<currentThreadCount>\d+?);' +
        '(?P<maxThreads>\d+?);(?P<numBusyConnections>\d+?);' +
        '(?P<maxPoolSize>\d+?);(?P<activeSessions>\d+?)',
        db, callbacks)

    discard = LogParser('^timestamp;currentThreadCount;maxThreads;numBusyConnections;maxPoolSize;activeSessions')

    parse_lines([jmx, discard], config['input'])

    # clean up the data
    c = db.cursor()
    # clean up entries outside of the timeslots
    c.execute('delete from logentries where timestamp < ?',
        (config['startTime'], ))
    c.execute('delete from logentries where timestamp > ?',
        (config['endTime'], ))

    # clean up doublets or other problems with the logfile
    c.close()

    # thread pool
    c = db.cursor()
    c.execute('select timestamp as "timestamp [timestamp]", ' +
        'currentThreadCount, maxThreads from logentries order by timestamp')
    report_threadpool(config['startTime'], config['endTime'], c.fetchall(),
        os.path.join(config['output'],
            config['host'] + '_thread_pool.png'),
        config['host'] + ': Thread Pool')
    c.close()

    # connection pool
    c = db.cursor()
    c.execute('select timestamp as "timestamp [timestamp]", ' +
        'numBusyConnections, maxPoolSize from logentries order by timestamp')
    report_connectionpool(config['startTime'], config['endTime'], c.fetchall(),
        os.path.join(config['output'],
            config['host'] + '_connection_pool.png'),
        config['host'] + ': C3PO Connection Pool')
    c.close()

    # active sessions
    c = db.cursor()
    c.execute('select timestamp as "timestamp [timestamp]", ' +
        'activeSessions from logentries order by timestamp')
    report_sessions(config['startTime'], config['endTime'], c.fetchall(),
        os.path.join(config['output'],
            config['host'] + '_active_sessions.png'),
        config['host'] + ': Active Sessions')
    c.close()


def usage():
    """
    Prints the script's usage guide.
    """
    print "Usage: plot_jmx.py input output"
    print "host = hostname"
    print "input = path to simulation.log file"
    print "output = path to simulation.png file"
    print "time-start = date in yyyy-MM-dd HH:mm:ss format"
    print "time-end = date in yyyy-MM-dd HH:mm:ss format"
    sys.exit(-1)


if __name__ == "__main__":
    if (len(sys.argv) != 6):
        usage()
    logging.basicConfig(
        filename='plot_error.log',
        level=logging.WARNING,
        format='%(asctime)s %(message)s'
    )
    suffix = os.path.basename(sys.argv[2]).split('.', 1)[0].split('-', 2)[2]
    with tarfile.open(sys.argv[2], 'r') as tar:
        fi = tar.extractfile('./jmx.txt.%s' % suffix)
        config = {
            'host': sys.argv[1],
            'input': fi,
            'output': sys.argv[3],
            'startTime': datetime.datetime.strptime(
                sys.argv[4], '%Y-%m-%d %H:%M:%S'),
            'endTime':  datetime.datetime.strptime(
                sys.argv[5], '%Y-%m-%d %H:%M:%S'),
        }

        main(config)
