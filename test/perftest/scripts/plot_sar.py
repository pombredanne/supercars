#!/usr/bin/env python
"""
For performance testing you need a clear picture about the utilization
of the machine your application is running on

This script helps you to analyse sar logs in order to extract information
about machine utilization. The information contained in the vmstat logs is
extracted and put into a in memory database for easy processing. This is of cause
a limiting factor but usually sufficient for the kind of systems and test 
durations I am facing. If you are testing really huge systems like a whole system
stack you might need to configure a file based database or you might prefer
a different approach.

Before you can start the analysing your log files you need to retrieve the sar
logs from your system. 

Before executing the script you need to configure start and end time of your test
and the path of the sar logs. Feel free to use this script as a basis for your work.

(c) Mark Fink, 2008 - 2012
This script is released under the Modified BSD License
Warranty in any form is excluded
"""

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


def report_netw(starttime, endtime, devdata, edevdata, reportfile, reporttitle):
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
    ylabel('network activity [in kB]')
    
    ts, rxkB, txkB = zip(*devdata)  # unpack
    ts2, rxerr, txerr, coll = zip(*edevdata)  # unpack

    # use HTML color names like:
    # http://www.html-color-names.com/color-chart.php
    plt1, = plot(ts, rxkB, 'Green')
    plt2, = plot(ts, txkB, 'Blue')
    axis([None,None,0,None])
    fig.autofmt_xdate()
    
    ax2 = twinx()  # use a second axis for waiting processes
    plt3, = plot(ts2, coll, 'Red')
    plt4, = plot(ts2, rxerr, 'Magenta')
    plt5, = plot(ts2, txerr, 'Orange')
    axis([None,None,0,None])
    ylabel('errors/s')
    ax2.yaxis.tick_right()

    # legend is a little more work since we use two y-axis
    legend([plt1, plt2, plt3, plt4, plt5], ['kB rec',
        'kB trans', 'collitions', 'rec error', 'trans error'],
        loc=0) # 0 for optimized legend placement

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
    #05:39:00 PM     IFACE   rxpck/s   txpck/s    rxkB/s    txkB/s   rxcmp/s   txcmp/s  rxmcst/s
    #05:39:05 PM        lo      0.00      0.00      0.00      0.00      0.00      0.00      0.00
    #05:39:05 PM      eth0      0.00      0.00      0.00      0.00      0.00      0.00      0.00
    #05:39:05 PM     wlan0      0.00      0.00      0.00      0.00      0.00      0.00      0.00
    #
    #05:39:00 PM     IFACE   rxerr/s   txerr/s    coll/s  rxdrop/s  txdrop/s  txcarr/s  rxfram/s  rxfifo/s  txfifo/s
    #05:39:05 PM        lo      0.00      0.00      0.00      0.00      0.00      0.00      0.00      0.00      0.00
    #05:39:05 PM      eth0      0.00      0.00      0.00      0.00      0.00      0.00      0.00      0.00      0.00
    #05:39:05 PM     wlan0      0.00      0.00      0.00      0.00      0.00      0.00      0.00      0.00      0.00    
    def timestamp(logstart, interval):
        # helper to create a generator for adding timestamps to 
        # parsed loglines
        # workaround missing nonlocal to implement closure
        nonlocal = {
            'logstart' : logstart,
            'interval': int(interval)
            }

        def gen(**kw_args):
            if 'rxpck' in kw_args and kw_args['iface'] == 'lo':
                # workaround for broken timestamps in sar log headers on centos
                nonlocal['logstart'] += timedelta(seconds=nonlocal['interval'])
            #ts = datetime.datetime.strptime(
            #    kw_args['ts'], '%I:%M:%S %p')
            #if not nonlocal['logstart'].time() == ts.time():
            #    nonlocal['logstart'] += timedelta(
            #        seconds=nonlocal['interval'])
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
    dev = LogParser('^(?P<ts>\d{2}:\d{2}:\d{2}( (AM|PM))?)\s+' + 
        '(?P<iface>\w+)\s+(?P<rxpck>[0-9.]+)\s+(?P<txpck>[0-9.]+)\s+' +
        '(?P<rxkB>[0-9.]+)\s+(?P<txkB>[0-9.]+)\s+(?P<rxcmp>[0-9.]+)' +
        '\s+(?P<txcmp>[0-9.]+)\s+(?P<rxmcst>[0-9.]+)\s+$',        
        db, callbacks, 'deventries')

    edev = LogParser('^(?P<ts>\d{2}:\d{2}:\d{2}( (AM|PM))?)\s+' +
        '(?P<iface>\w+)\s+(?P<rxerr>[0-9.]+)\s+(?P<txerr>[0-9.]+)\s+' +
        '(?P<coll>[0-9.]+)\s+(?P<rxdrop>[0-9.]+)\s+' +
        '(?P<txdrop>[0-9.]+)\s+(?P<txcarr>[0-9.]+)\s+' +
        '(?P<rxfram>[0-9.]+)\s+(?P<rxfifo>[0-9.]+)\s+' +
        '(?P<txfifo>[0-9.]+)\s+$',
        db, callbacks, 'edeventries')

    # do not report these lines as errors
    discard = LogParser('^(?P<ts>\d{2}:\d{2}:\d{2}( (AM|PM)?))\s+IFACE|'+
        '^Average:|^Linux')

    parse_lines([dev, edev, discard], config['input'])
    
    # clean up the data
    c = db.cursor()
    # clean up entries outside of the timeslots
    c.execute('delete from deventries where timestamp < ?',
        (config['startTime'], ))
    c.execute('delete from deventries where timestamp > ?',
        (config['endTime'], ))
    c.execute('delete from edeventries where timestamp < ?',
        (config['startTime'], ))
    c.execute('delete from edeventries where timestamp > ?',
        (config['endTime'], ))

    # clean up doublets or other problems with the logfile
    c.close()
    
    # extract the data for the report(s)
    c = db.cursor()
    d = db.cursor()
    # Sar
    c.execute('select timestamp as "timestamp [timestamp]", ' +
        'rxkB, txkB from deventries where iface=? ' +
        'order by timestamp', ('eth0',))
    d.execute('select timestamp as "timestamp [timestamp]", ' +
        'rxerr, txerr, coll from edeventries where iface=? ' +
        'order by timestamp', ('eth0',))
    report_netw(config['startTime'], config['endTime'], c.fetchall(), 
        d.fetchall(), 
        os.path.join(config['output'],
            config['host'] + '_network.png'), 
        config['host'] + ': Network utilization')
    c.close()
    d.close()


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
        fi = tar.extractfile('./sar.txt.%s' % suffix)
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

