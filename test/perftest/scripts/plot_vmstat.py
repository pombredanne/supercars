#!/usr/bin/env python
"""
For performance testing you need a clear picture about the utilization
of the machine your application is running on

This script helps you to analyse vmstat logs in order to extract information
about machine utilization. The information contained in the vmstat logs is
extracted and put into a in memory database for easy processing. This is of cause
a limiting factor but usually sufficient for the kind of systems and test
durations I am facing. If you are testing really huge systems like a whole system
stack you might need to configure a file based database or you might prefer
a different approach.

Before you can start the analysing your log files you need to retrieve the vmstat
logs from your system.

Before executing the script you need to configure start and end time of your test
and the path of the vmstat logs. Feel free to use this script as a basis for your work.

(c) Mark Fink, 2008 - 2012
This script is released under the MIT License
Warranty in any form is excluded
"""

import logging
import sqlite3
from datetime import datetime, timedelta
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


def report_cpu(starttime, endtime, data, reportfile, reporttitle):
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
    ylabel('CPU utilization [%]')

    ts, user, sys, idle, wait = zip(*data)  # unpack
    # use HTML color names like:
    # http://www.html-color-names.com/color-chart.php
    plot(ts, user, 'Red', label='user')
    plot(ts, sys, 'Lime', label='system')
    plot(ts, idle, 'Gold', label='idle')
    plot(ts, wait, 'Blue', label='wait IO')

    axis([None, None, 0, None])
    legend(loc=0)  # 0 for optimized legend placement
    fig.autofmt_xdate()

    savefig(reportfile)

    # cleanup
    clf()
    cla()


def report_io(starttime, endtime, data, reportfile, reporttitle):
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

    ts, bi, bo = zip(*data)  # unpack
    # use HTML color names like:
    # http://www.html-color-names.com/color-chart.php
    plot(ts, bi, 'Red', label='in')
    plot(ts, bo, 'Lime', label='out')

    axis([None, None, 0, None])
    legend(loc=0)  # 0 for optimized legend placement
    fig.autofmt_xdate()

    savefig(reportfile)

    # cleanup
    clf()
    cla()


def report_health(starttime, endtime, data, reportfile, reporttitle):
    """Create the report file, this part is application specific."""
    # Note: I use Pylab, Pylab is a procedural interface to the
    # matplotlib object-oriented plotting library. Of cause if you
    # prefere the original matplotlib style or any other plotting tool
    # you can use it here
    ax1 = subplot(111)
    fig = figure()

    title(reporttitle)

    tz = pytz.timezone('Europe/Berlin').localize(datetime.datetime.now()).strftime('%z')
    xlabel('reported time: %s to %s [UTC %s]' % (starttime, endtime, tz),
        fontsize='small', x=1.0, ha='right')
    ylabel('Context switches/s')

    ts, r, cs = zip(*data)  # unpack
    # use HTML color names like:
    # http://www.html-color-names.com/color-chart.php
    plt1, = plot(ts, cs, 'Lime')
    axis([None, None, 0, None])
    fig.autofmt_xdate()

    ax2 = twinx()  # use a second axis for waiting processes
    plt2, = plot(ts, r, 'Red')
    ylabel('waiting processes')
    ax2.yaxis.tick_right()

    # legend is a little more work since we use two y-axis
    legend([plt1, plt2], ['context switches', 'waiting processes'],
        loc=0)  # 0 for optimized legend placement

    savefig(reportfile)

    # cleanup
    clf()
    cla()


def report_mem(starttime, endtime, data, reportfile, reporttitle):
    """Create the report file, this part is application specific."""
    # Note: I use Pylab, Pylab is a procedural interface to the
    # matplotlib object-oriented plotting library. Of cause if you
    # prefere the original matplotlib style or any other plotting tool
    # you can use it here
    ax1 = subplot(111)
    fig = figure()

    title(reporttitle)

    tz = pytz.timezone('Europe/Berlin').localize(datetime.datetime.now()).strftime('%z')
    xlabel('reported time: %s to %s [UTC %s]' % (starttime, endtime, tz),
        fontsize='small', x=1.0, ha='right')
    ylabel('free memory [in MB]')

    #print 'data: %s' % data

    ts, free, si, so = zip(*data)  # unpack
    free = [float(x) / 1024 for x in free]
    # use HTML color names like:
    # http://www.html-color-names.com/color-chart.php

    plt1, = plot(ts, free, 'Red')
    axis([None, None, 0, 12000])
    fig.autofmt_xdate()

    ax2 = twinx()  # use a second axis for waiting processes
    plt2, = plot(ts, si, 'Lime')
    plt3, = plot(ts, so, 'Blue')
    axis([None, None, 0, None])
    ylabel('pages/s')
    ax2.yaxis.tick_right()

    # legend is a little more work since we use two y-axis
    legend([plt1, plt2, plt3], ['free mem', 'page-in', 'page-out'],
        loc=0)  # 0 for optimized legend placement

    savefig(reportfile)

    # cleanup
    clf()
    cla()


######################################################################
# It would be possible to store the non application specific parts of
# the script like parse_lines and LogParser in a central file.
# I currently prefere a version that has every thing on board.

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
                    ') values (' + ', '.join(['?'] * (len(values) +
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
    #20111201 152900 interval 5 sec
    #procs -----------memory---------- ---swap-- -----io---- -system-- ----cpu ----
    # r  b   swpd   free   buff  cache   si   so    bi    bo   in   cs us sy id wa
    # 2  0      0 180152 472892 1843548    0    0     4    10   23   18  9  6 84  0
    #procs -----------memory---------- ---swap-- -----io---- --system-- -----cpu------
    # r  b   swpd   free   buff  cache   si   so    bi    bo   in   cs us sy id wa st
    # 2  0      0 11116488 835728 1764956    0    0     0     5    1    1  0  0 99  0  0
    #procs -----------memory---------- ---swap-- -----io---- -system-- ----cpu----
    # r  b   swpd   free   buff  cache   si   so    bi    bo   in   cs us sy id wa
    # 0  0      0 2172996 551736 688480    0    0   218    21 5945  104  7  4 84  6
    def timestamp(logstart, interval):
        # helper to create a generator for adding timestamps to
        # parsed loglines
        # workaround nonlocal to implement missing closure
        nonlocal = {
            'logstart': logstart,
            'interval': int(interval)
            }

        def gen(**kw_args):
            nonlocal['logstart'] += timedelta(
                seconds=nonlocal['interval'])
            return nonlocal['logstart']
        return gen

    # central result database which is hold in memory
    db = sqlite3.connect(':memory:',
        detect_types=sqlite3.PARSE_COLNAMES)

    # read logstart and interval
    match = re.compile('^(?P<logstart>\d{8} \d{6})' +
        ' interval (?P<interval>\d+) sec').match(
        config['input'].readline()).groupdict()

    callbacks = {'timestamp': timestamp(
        datetime.datetime.strptime(match['logstart'], '%Y%m%d %H%M%S'),
        match['interval'])
    }

    # parse the data from the logfiles
    vmstat = LogParser('^\s+(?P<r>\d+)\s+(?P<b>\d+)\s+' +
        '(?P<swpd>\d+)\s+(?P<free>\d+)\s+(?P<buff>\d+)\s+' +
        '(?P<cache>\d+)\s+(?P<si>\d+)\s+(?P<so>\d+)\s+(?P<bi>\d+)' +
        '\s+(?P<bo>\d+)\s+(?P<iin>\d+)\s+(?P<cs>\d+)\s+(?P<us>\d+)' +
        '\s+(?P<sy>\d+)\s+(?P<id>\d+)\s+(?P<wa>\d+)\s*(?P<st>\d+)?',
        db, callbacks)

    discard = LogParser('^ r  b   swpd|^procs ---')

    parse_lines([vmstat, discard], config['input'])

    # clean up the data
    c = db.cursor()
    # clean up entries outside of the timeslots
    c.execute('delete from logentries where timestamp < ?',
        (config['startTime'], ))
    c.execute('delete from logentries where timestamp > ?',
        (config['endTime'], ))

    # clean up doublets or other problems with the logfile
    c.close()

    # extract the data for the report(s)
    # CPU
    c = db.cursor()
    c.execute('select timestamp as "timestamp [timestamp]", ' +
        'us, sy, id, wa from logentries order by timestamp')
    report_cpu(config['startTime'], config['endTime'], c.fetchall(),
        os.path.join(config['output'],
            config['host'] + '_cpu.png'),
        config['host'] + ': CPU utilization')
    #c.close()

    #c = db.cursor()
    # IO
    c.execute('select timestamp as "timestamp [timestamp]", ' +
        'bi, bo from logentries order by timestamp')
    report_io(config['startTime'], config['endTime'], c.fetchall(),
        os.path.join(config['output'],
            config['host'] + '_io.png'),
        config['host'] + ': IO')

    # MEM
    c.execute('select timestamp as "timestamp [timestamp]", ' +
        'free, si, so from logentries order by timestamp')
    report_mem(config['startTime'], config['endTime'], c.fetchall(),
        os.path.join(config['output'],
            config['host'] + '_mem.png'),
        config['host'] + ': Memory utilization')

    # Health
    c.execute('select timestamp as "timestamp [timestamp]", ' +
        'r, cs from logentries order by timestamp')
    report_health(config['startTime'], config['endTime'], c.fetchall(),
        os.path.join(config['output'],
            config['host'] + '_health.png'),
        config['host'] + ': System health')
    c.close()


def usage():
    """
    Prints the script's usage guide.
    """
    print "Usage: vmstat.py input output"
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
    #files = glob.glob(sys.argv[2])
    #fs1.sort(key=extract_filenumber, reverse=True)
    #fi = fileinput.input(files) # iterate over the lines of all files
    suffix = os.path.basename(sys.argv[2]).split('.', 1)[0].split('-', 2)[2]
    with tarfile.open(sys.argv[2], 'r') as tar:
        fi = tar.extractfile('./vmstat.txt.%s' % suffix)

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
