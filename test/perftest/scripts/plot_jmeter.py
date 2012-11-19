#!/usr/bin/env python
"""
For performance testing you need a clear understanding of the transaction rates
of your target system configuration. From this information you need to design a
simplified load model for your performance test.

This script helps you to analyse access logs in order to extract information about
transaction rates per hour. The information contained in the access logs is
extracted and put into a in memory database for easy processing. This is of cause
a limiting factor but usually sufficient for the kind of systems and test 
durations I am facing. If you are testing really huge systems like a whole system
stack you might need to configure a file based database or you might prefer
a different approach.

Before you can start the analysing your log files you need to retrieve the access
logs from the productive system. 

Before executing the script you need to configure start and end time of your test
and the path of the access logs. You also need to configure regular expressions
to extract the data from the access logs and the report format. A decent command
of SQL is required so you can formulate the SQL queries which select the data
for your report. Feel free to use this script as a basis for your work.

(c) Mark Fink, 2008 - 2012
This script is released under the Modified BSD License
Warranty in any form is excluded
"""

import logging
import sqlite3
from datetime import datetime, timedelta
import pytz
from matplotlib.ticker import MaxNLocator
from pylab import *

import fileinput
import glob
import re
import os
import tarfile
from chameleon.zpt.loader import TemplateLoader
import xlrd


here = lambda x: os.path.abspath(os.path.join(os.path.dirname(__file__), x))

def extract_filenumber(filename):
    """this helper function sorts the log files into the correct order"""
    n = filename.split('.')[-1]
    if n.isalpha():
        return 0
    else:
        return int(n)

def report_hour(starttime, endtime, data, reportfile, reporttitle, request):
    """Create the report file, this part is application specific."""
    title(reporttitle)
    gcf().subplots_adjust(bottom=0.18)
    
    tz = pytz.timezone('Europe/Berlin').localize(datetime.datetime.now()).strftime('%z')
    xlabel('reported time: %s to %s [UTC %s]' % (starttime, endtime, tz) +
        '\n' + request, fontsize='small', x=1.0, ha='right')
    ylabel('Transactions per hour')
   
    names  = [x[0][5:] for x in data]
    values = zip(*data)[1]
   
    ind = np.arange(len(data))+1.0 # center bars on the x-axis ticks
   
    #width = 1.0 # the width of the bars (1 is full bar)
    bar(ind, values, align='center', width=1.0, linewidth=None, yerr=None)

    # add a grid to the subplot
    axes().yaxis.grid(True, linestyle='--', which='major', color='grey', alpha=0.25)
   
    xticks(ind, names, rotation=90, fontsize=6)

    #TODO: legend

    savefig(reportfile)
   
    # cleanup
    clf()
    cla()


def report_rt(starttime, endtime, data, reportfile, reporttitle, request):
    """Create the report file, this part is application specific."""
    # Note: I use Pylab, Pylab is a procedural interface to the
    # matplotlib object-oriented plotting library. Of cause if you 
    # prefere the original matplotlib style or any other plotting tool
    # you can use it here
    title(reporttitle)
    gcf().subplots_adjust(bottom=0.15)
    fig = figure()
    
    tz = pytz.timezone('Europe/Berlin').localize(datetime.datetime.now()).strftime('%z')
    xlabel('reported time: %s to %s [UTC %s]' % (starttime, endtime, tz) +
        '\n' + request, fontsize='small', x=1.0, ha='right')
    ylabel('Response Time [in s]')

    ts, rt = zip(*data)  # unpack
    # use HTML color names like:
    # http://www.html-color-names.com/color-chart.php
    plot(ts, rt, 'Blue', label='rt')

    axis([None,None,0,None])
    #legend(loc=0) # 0 for optimized legend placement
    fig.autofmt_xdate()

    savefig(reportfile)
   
    # cleanup
    clf()
    cla()


def report_perc(starttime, endtime, data, reportfile, reporttitle, request):
    """Create the report file, this part is application specific."""
    # Note: I use Pylab, Pylab is a procedural interface to the
    # matplotlib object-oriented plotting library. Of cause if you 
    # prefere the original matplotlib style or any other plotting tool
    # you can use it here
    title(reporttitle)
    gcf().subplots_adjust(bottom=0.15)
    
    tz = pytz.timezone('Europe/Berlin').localize(datetime.datetime.now()).strftime('%z')
    xlabel('reported time: %s to %s [UTC %s]' % (starttime, endtime, tz) +
        '\n' + request, fontsize='small', x=1.0, ha='right')
    ylabel('Response Time [in s]')

    rt = zip(*data)[0]  # unpack
    p = [float(x) * 100.0 / len(rt)  for x in range(1, len(rt)+1)]

    plot(p, rt, 'Blue', label='rt')

    axis([None,None,0,None])
    axes().xaxis.grid(True, linestyle='-', which='major',
        color='lightgrey')
    # tick at all full 10 percentiles
    axes().xaxis.set_major_locator(MaxNLocator(11))

    savefig(reportfile)
   
    # cleanup
    clf()
    cla()


def report_overview(starttime, endtime, data, reportfile, reporttitle,
    scenario):
    """Create the report file, this part is application specific."""
    # Note: I use ZPT. Of cause if you would prefere something else
    # you can use it here
    pt_loader = TemplateLoader(here('./templates'), auto_reload=True)
    template = pt_loader.load('response_times.pt')
    result = template(starttime=starttime, endtime=endtime,
        data=data, reporttitle=reporttitle, scenario=scenario).encode(
        'ISO-8859-1')
    fo = open(reportfile, 'w')
    fo.write(result)
    fo.close()


######################################################################
# It would be possible to store the non application specific parts of
# the script like parse_lines and LogParser in a central file.
# I currently prefere a version that has every thing on board.

def parse_lines(logParsers, fileinp):
    """parse lines from the fileinput and send them to the logparser"""
    while 1:
        line = fileinp.readline()
        #print line.rstrip()
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


def read_loadmodel(filename):
    """read testplan from Excel file"""
    wb = xlrd.open_workbook(filename)
    sh = wb.sheet_by_index(0)
    
    nodes = [] # transform into a list
    for rownum in range(sh.nrows):
        nodes.append(sh.row_values(rownum))
    return nodes[2][0], nodes[4:]


def main(config):
    """The main part contains the configuration that fits your analysis situation
    this is by nature application specific. In other words adjust everything in
    here so it fits your needs!"""
    #timeStamp|elapsed|label|responseCode|responseMessage|threadName|dataType|success|failureMessage|bytes|Latency
    #1323421238878|36|/speakers/|200|OK|Site - Speakers 2-1|text|true||18690|34
    
    def timestamp(**kw_args):
        #print 'kw_Args: ' + str(kw_args)
        # convert the timestamp in datetime format
        ts = datetime.datetime.fromtimestamp(
            float(kw_args['tsms'][:-3]))
        #ts += datetime.timedelta(milliseconds=
        #    int(kw_args['tsms'][-3:]))
        return ts

    def startdate(**kw_args):
        # convert the timestamp into format required for stats
        ts = datetime.datetime.fromtimestamp(
            float(kw_args['tsms'][:-3]))
        return ts.strftime('%Y-%m-%d %H:%M:%S')

    def request_time(**kw_args):
        # convert ms to sec
        return float(kw_args['elapsed']) / 1000.0

    # central result database which is hold in memory
    db = sqlite3.connect(':memory:', 
        detect_types=sqlite3.PARSE_COLNAMES)

    callbacks = {'timestamp': timestamp, 'startdate': startdate,
        'request_time': request_time}

    # parse the data from the logfiles
    #1323426522802|23|/static/tu|200|OK|Site - Speakers 2-1|bin|true||8638|23
    #1323426465891|42|/speakers/|200|OK|Site - Speakers 2-1|text|true||18690|40
    #timeStamp,elapsed,label,responseCode,responseMessage,threadName,dataType,success,failureMessage,bytes,Latency
    #1334651452512,197,interpolateTemperatureHistoriesInDatetimeRangeToNumberOfPoints,200,OK,Thread Group 3-1,text,true,,18850,0
    #1334654769310,62,getSensorAssignmentsWithTemperatureAggregations,200,OK,Thread Group 1-1,text,true,,4201,0
    '''
    jmeter = LogParser('^(?P<tsms>\d+)[,](?P<elapsed>\d+)[,]' +
        '(?P<request>[^,]+)[,](?P<responsecode>\d+)[,]' +
        '(?P<responsemessage>[^,]+)[,](?P<threadname>[^,]+)[,]' +
        '(?P<datatype>[^,]+)[,](?P<success>[^,]+)[,]' +
        '(?P<failuremessage>[^,]*)[,](?P<bytes>\d+)[,](?P<latency>\d+)$',
        db, callbacks)'''
    #timeStamp,elapsed,label,responseCode,responseMessage,threadName,dataType,success,failureMessage,bytes,Latency
    jmeter = LogParser('^(?P<tsms>\d+)[,](?P<elapsed>\d+)[,](?P<request>[^,]+)[,](?P<responsecode>\d+)[,](?P<responsemessage>[^,]+)[,](?P<threadname>[^,]+)[,](?P<datatype>[^,]+)[,](?P<success>[^,]+)[,](?P<failuremessage>[^,]*)[,](?P<bytes>\d+)[,](?P<latency>\d+)(?P<sth>.*)$',
        db, callbacks)

    discard = LogParser('^timeStamp[,]')

    parse_lines([jmeter, discard], config['input'])

    # fill timeslots into database, this is neccessary in order to have
    # timeslots with zero amount of requests
    c = db.cursor()
    c.execute('create table timeslots(timeslot, cnt)')
    #s = datetime.strptime(starttime[:13], '%Y-%m-%d %H')
    s = config['startTime']
    s = s - datetime.timedelta(minutes=s.minute, seconds=s.second,
        microseconds=s.microsecond)    
    #while s < datetime.strptime(endtime, '%Y-%m-%d %H:%M:%S'):
    while s < config['endTime']:
        c.execute('insert into timeslots(timeslot, cnt) values (?, ?)',
            (s.strftime('%Y-%m-%d %H') , 0))
        s = s + timedelta(hours=1)
    c.close()
   
    # clean up the data
    c = db.cursor()
    
    c.execute('delete from logentries where timestamp < ?',
        (config['startTime'], ))
    c.execute('delete from logentries where timestamp > ?',
        (config['endTime'], ))
    
    c.close()
    # TODO: clean up doublets or other problems with the logfile
   
    # loop over all requests and create images
    c = db.cursor()
    c.execute('select distinct(request) from logentries')
    requests = zip(*c.fetchall())[0]
    c.close()

    # extract the data for the overview report
    overview = []
    scenario, loadmodel = read_loadmodel(config['loadmodel'])

    for step in loadmodel:
        c = db.cursor()
        c.execute('select avg(elapsed) as "avg [real]", ' +
            'count(elapsed) from logentries where request=?',
            (step[0],))
        avg, count = c.fetchone()
        seconds = (config['endTime'] - config['startTime']).total_seconds()
        if count:
            # if we have measurements
            c.execute('select elapsed as "p90 [real]" ' +
                'from logentries where request=? ORDER BY CAST(elapsed as REAL) ' + 
                'LIMIT 1 OFFSET round(0.9*(select count(elapsed) from ' +
                'logentries where request=?))', 
                (step[0], step[0]))
            p90 = c.fetchone()[0]
            c.execute('select count(responsecode) ' +
                'from logentries where request=? ' +
                'and not failuremessage=""', (step[0],))
            errors = c.fetchone()[0]
            overview.append((step[0], '%.0f' % step[1], '%.3f' % step[2], 
                '%.3f' % (float(avg)/1000), '%.3f' % (float(p90)/1000), 
                '%.0f%%' % round(float(count)*3600/seconds/float(step[1])*100), 
                '%.0f%%' % round(float(errors)/float(step[1])*100)))
        else:
            overview.append((step[0], '%.0f' % step[1], '%.3f' % step[2], 
                '--', '--', '0%', '0%'))        
        c.close()

    report_overview(config['startTime'], config['endTime'], overview,
        os.path.join(config['output'], 
            config['host'] + '_responsetimes.html'),
        'Test Result Overview', scenario)
    
    for r in requests:   
        # extract the data for the report
        c = db.cursor()
        name = r.replace('/', '-')
        # rt
        c = db.cursor()
        c.execute('select timestamp as "timestamp [timestamp]", ' +
            'request_time from logentries ' +
            'where request=? '
            'order by timestamp', (r,))
        report_rt(config['startTime'], config['endTime'], c.fetchall(), 
            os.path.join(config['output'], 
                config['host'] + '_rt_' + name + '.png'),
            'Response Time', r)
        
        # hourly
        c.execute('select tf, sum(cnt) from (' +
            'select (substr(startdate,1,13)) as tf, count(request) as cnt ' +
            'from logentries where request=? group by tf ' +
            'union select timeslot as tf, cnt from timeslots) ' +
            'group by tf', (r,))
        report_hour(config['startTime'], config['endTime'], c.fetchall(),
            os.path.join(config['output'], 
                config['host'] + '_hourly_' + name + '.png'),
            'Load distributed over time', r)

        # percentile
        c = db.cursor()
        c.execute('select request_time from logentries ' + 
            'where request=? '
            'order by request_time', (r,))
        report_perc(config['startTime'], config['endTime'], c.fetchall(), 
            os.path.join(config['output'], 
                config['host'] + '_perc_' + name + '.png'),
            'Response Time Percentiles', r)
   
        # clean up
        c.close()
    

def usage():
    """
    Prints the script's usage guide.
    """
    print "Usage: plot_jmeter.py host input outputfolder loadmodel start stop"
    print "host = hostname"
    print "input = path to jmeter-logs.tgz file"
    print "outputfolder = path to folder for plot (*.png) files"
    print "loadmodel = path to loadmodel.xls file"
    print "time-start = date in yyyy-MM-dd HH:mm:ss format"
    print "time-end = date in yyyy-MM-dd HH:mm:ss format"
    sys.exit(-1)


if __name__ == "__main__":
    if (len(sys.argv) != 7):
        usage()
    logging.basicConfig(
        filename=os.path.join(sys.argv[3], '../plot_error.log'),
        level=logging.WARNING,
        format='%(asctime)s %(message)s'
    )
    suffix = os.path.basename(sys.argv[2]).split('.', 1)[0].split('-', 2)[2]
    with tarfile.open(sys.argv[2], 'r') as tar:
        fi = tar.extractfile('results.txt.%s' % suffix)
        config = {
            'host': sys.argv[1],
            'input': fi,
            'output': sys.argv[3],
            'loadmodel': sys.argv[4],
            'startTime': datetime.datetime.strptime(
                sys.argv[5], '%Y-%m-%d %H:%M:%S'),
            'endTime':  datetime.datetime.strptime(
                sys.argv[6], '%Y-%m-%d %H:%M:%S'),
        }

        main(config)
        