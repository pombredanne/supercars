#!/usr/bin/env python
"""
For performance testing you need a clear picture about the utilization
of the machine your application is running on.

This script helps you to analyse sar logs in order to extract information
about machine utilization. The information contained in the top logs is
extracted and put into a in memory database for easy processing. This is of cause
a limiting factor but usually sufficient for the kind of systems and test 
durations I am facing. If you are testing really huge systems like a whole system
stack you might need to configure a file based database or you might prefer
a different approach.

Before you can start the analysing your log files you need to retrieve the top
logs from your system. 

Before executing the script you need to configure start and end time of your test
and the path of the top logs. Feel free to use this script as a basis for your work.

(c) Mark Fink, 2008 - 2012
This script is released under the Modified BSD License
Warranty in any form is excluded
"""

import operator
import logging
import sqlite3
from datetime import datetime, timedelta
import pytz
from pylab import *

import fileinput
import glob
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


def report_top(starttime, endtime, data, reportfile, reporttitle):
    """Create the report file, this part is application specific."""
    # Note: I use Pylab, Pylab is a procedural interface to the
    # matplotlib object-oriented plotting library. Of cause if you 
    # prefere the original matplotlib style or any other plotting tool
    # you can use it here
    ax1 = subplot(111)
    fig=figure()

    title(reporttitle)

    tz = pytz.timezone('Europe/Berlin').localize(datetime.datetime.now()).strftime('%z')
    xlabel('reported time: %s to %s [UTC %s]' % (starttime, endtime, tz),
        fontsize='small', x=1.0, ha='right')
    ylabel('CPU utilization [%]')

    # use HTML color names like:
    # http://www.html-color-names.com/color-chart.php
    colors = ['Red', 'Green', 'Gold', 'Magenta', 'Grey', 'Blue', 
        'Lime', 'Indigo', 'Plum', 'DeepSkyBlue']
    last = [0] * len(data[0][1])
    plots = []
    labels = zip(*data[::-1])[0][:-1]

    # loop over processes
    for i, process in enumerate(data[1:]):
        new = map(operator.add, last, process[1])
        plots.extend(plot(data[0][1], new, color=colors[i],
            label=process[0]))
        fill_between(data[0][1], new, last, color=colors[i])
        last = new
        
    axis([None,None,0,None])
    legend(plots[::-1], labels, loc=0, labelspacing=0.1) #reversed(plots), 
    fig.autofmt_xdate()

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
    def timestamp(logstart, interval):
        # helper to create a generator for adding timestamps to 
        # parsed loglines
        # workaround missing nonlocal to implement closure
        nonlocal = {
            'logstart' : logstart,
            'interval': int(interval)
            }

        def gen(**kw_args):
            if 'ts' in kw_args:
                ts = datetime.datetime.strptime(
                    kw_args['ts'], '%H:%M:%S').time()
                low = (nonlocal['logstart'] - 
                    datetime.timedelta(seconds=1)).time()
                high = (nonlocal['logstart'] + 
                    datetime.timedelta(seconds=1)).time()
                if not (low <= ts <= high):
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
    #  PID USER      PR  NI  VIRT  RES  SHR S %CPU %MEM    TIME+  COMMAND            
    # 2403 mark      20   0  450m 184m  35m S   14  4.7  66:22.29 chromium-browse
    # centos
    #  PID USER      PR  NI  VIRT  RES  SHR S %CPU %MEM    TIME+  COMMAND            
    #    1 root      15   0 10372  696  584 S  0.0  0.0   0:00.60 init               
    #  PID USER      PR  NI  VIRT  RES  SHR S %CPU %MEM    TIME+  COMMAND            
    # 4343 root       0 -20 33300 6232 2160 S    0  0.0   1044:25 scopeux<<<
    # 9251 jadmin    18   0  399m  72m  20m S    0  0.4   1050:09 java<<<

    top = LogParser('^\s*(?P<pid>\d+)\s+(?P<user>[\w\-_]+)\s+' + 
        '(RT|\-?\d+)\s+\-?\d+\s+(?P<virt>[\d.]+m?)\s+[\d.]+m?' +
        '\s+[\d.]+m?\s+\w+\s+(?P<cpu>\d+\.?\d*)\s+[0-9.]+\s+' +
        '\d+:\d{2}(\.\d{2})?\s+(?P<command>.*[^\s])\s*$',
        db, callbacks)
    #top - 17:39:05 up  6:58,  2 users,  load average: 0.42, 0.28, 0.19
    clock = LogParser('^top - (?P<ts>\d{2}:\d{2}:\d{2}) up.+$',
        callbacks=callbacks)

    # do not report these lines as errors
    #Tasks: 186 total,   1 running, 184 sleeping,   0 stopped,   1 zombie
    #Cpu(s): 17.7%us, 13.0%sy,  0.0%ni, 68.7%id,  0.6%wa,  0.0%hi,  0.0%si,  0.0%st
    #Mem:   4053696k total,  2531396k used,  1522300k free,   530024k buffers
    #Swap:        0k total,        0k used,        0k free,   878988k cached
    #  PID USER      PR  NI  VIRT  RES  SHR S %CPU %MEM    TIME+  COMMAND            
    discard = LogParser('^Tasks:|^Cpu|^Mem:|^Swap:|^  PID USER')

    parse_lines([top, clock, discard], config['input'])

    # clean up the data
    c = db.cursor()
    # clean up entries outside of the timeslots
    c.execute('delete from logentries where timestamp < ?',
        (config['startTime'], ))
    c.execute('delete from logentries where timestamp > ?',
        (config['endTime'], ))
    
    # clean up doublets or other problems with the logfile
    c.close()
    
    '''
    c = db.cursor()
    c.execute('select * from logentries')
    print 'logs: %s' % c.fetchall()
    c.close()
    '''
    
    # extract the data for the report(s)
    # commands contains the top 9 processes
    data = []
    c = db.cursor()
    c.execute('select command, sum(cpu) as cpu from logentries ' +
        'group by command ' +
        'order by cpu desc')
    commands = zip(*c.fetchmany(size=9))[0]
    # timestamp & others
    c.execute('select timestamp as "timestamp [timestamp]", ' +
        'sum(cpu) as cpu from logentries where '
        'command NOT IN ("%s") ' % '", "'.join(commands) +
        'group by timestamp order by timestamp')
    timestamp, others = zip(*c.fetchall())
    # insert missing zero values
    for ts in timestamp:
        for command in commands:
            c.execute('insert into logentries(timestamp, command, ' +
                'cpu) values (?, ?, ?)', (ts, command, 0))
    data.append(('timestamp', timestamp))
    # CPU utilization for commands
    for command in commands:
        c.execute('select sum(cpu) as cpu from logentries where command=?' +
            'group by timestamp order by timestamp', (command,))
        data.append((command, zip(*c.fetchall())[0]))
    data.append(('all other processes', others))

    report_top(config['startTime'], config['endTime'], data, 
        os.path.join(config['output'],
            config['host'] + '_top.png'), 
        config['host'] + ': CPU utilization by process')
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
    suffix = os.path.basename(sys.argv[2]).split('.', 1)[0].split('-', 2)[2]
    with tarfile.open(sys.argv[2], 'r') as tar:
        fi = tar.extractfile('./top.txt.%s' % suffix)
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

