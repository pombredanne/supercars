#!/usr/bin/env python

"""
The original version by Sujit Pal from:
http://sujitpal.blogspot.com/2006/08/charting-jvm-garbage-collection.html

Made the gcview script work with Python 2.5+ including some other minor corrections
by Mark Fink End of 2009, rework in 2010. 
Added tgz file processing, and PrintGCDateStamps support in 2012
"""

import os
import tarfile
import sys
import re
import time
from stat import *
from pylab import *


def parse(line):
    """
    Parses an input line from the logfile into a set of tokens and returns them.

    I decided to use -XX:+PrintHeapAtGC for logging Gc informationafter
    experiencing some problems with -XX:+PrintGCDetails

    sample log entry from OpenJDK Runtime Environment 
    (IcedTea6 1.10.2) (6b22-1.10.2-0ubuntu1~11.04.1):
{Heap before GC invocations=1 (full 0):
 PSYoungGen      total 18432K, used 15808K [0x9ef20000, 0xa03b0000, 0xb3920000)
  eden space 15808K, 100% used [0x9ef20000,0x9fe90000,0x9fe90000)
  from space 2624K, 0% used [0xa0120000,0xa0120000,0xa03b0000)
  to   space 2624K, 0% used [0x9fe90000,0x9fe90000,0xa0120000)
 PSOldGen        total 42240K, used 0K [0x75b20000, 0x78460000, 0x9ef20000)
  object space 42240K, 0% used [0x75b20000,0x75b20000,0x78460000)
 PSPermGen       total 16384K, used 1924K [0x6db20000, 0x6eb20000, 0x75b20000)
  object space 16384K, 11% used [0x6db20000,0x6dd01048,0x6eb20000)
0.305: [GC 15808K->15686K(60672K), 0.0252860 secs]
Heap after GC invocations=1 (full 0):
 PSYoungGen      total 18432K, used 2610K [0x9ef20000, 0xa1320000, 0xb3920000)
  eden space 15808K, 0% used [0x9ef20000,0x9ef20000,0x9fe90000)
  from space 2624K, 99% used [0x9fe90000,0xa011cb38,0xa0120000)
  to   space 2624K, 0% used [0xa1090000,0xa1090000,0xa1320000)
 PSOldGen        total 42240K, used 13075K [0x75b20000, 0x78460000, 0x9ef20000)
  object space 42240K, 30% used [0x75b20000,0x767e4ef0,0x78460000)
 PSPermGen       total 16384K, used 1924K [0x6db20000, 0x6eb20000, 0x75b20000)
  object space 16384K, 11% used [0x6db20000,0x6dd01048,0x6eb20000)
}

    Sample log entry:
{Heap before GC invocations=4 (full 3):
 def new generation   total 672000K, used 576000K [0x2dcd0000, 0x5cad0000, 0x5cad0000)
  eden space 576000K, 100% used [0x2dcd0000, 0x50f50000, 0x50f50000)
  from space 96000K,   0% used [0x56d10000, 0x56d10000, 0x5cad0000)
  to   space 96000K,   0% used [0x50f50000, 0x50f50000, 0x56d10000)
 tenured generation   total 768000K, used 626532K [0x5cad0000, 0x8b8d0000, 0x8b8d0000)
   the space 768000K,  81% used [0x5cad0000, 0x82ea91a8, 0x82ea9200, 0x8b8d0000)
 compacting perm gen  total 131072K, used 20K [0x8b8d0000, 0x938d0000, 0x938d0000)
   the space 131072K,   0% used [0x8b8d0000, 0x8b8d5188, 0x8b8d5200, 0x938d0000)
    ro space 8192K,  74% used [0x938d0000, 0x93eca2a8, 0x93eca400, 0x940d0000)
    rw space 12288K,  59% used [0x940d0000, 0x947e7878, 0x947e7a00, 0x94cd0000)
63.097: [GC, 2.7137000 secs]
65.811: [Full GC 1439966K->626649K(1440000K), 2.0454570 secs]
Heap after GC invocations=5 (full 4):
 def new generation   total 672000K, used 0K [0x2dcd0000, 0x5cad0000, 0x5cad0000)
  eden space 576000K,   0% used [0x2dcd0000, 0x2dcd0000, 0x50f50000)
  from space 96000K,   0% used [0x50f50000, 0x50f50000, 0x56d10000)
  to   space 96000K,   0% used [0x56d10000, 0x56d10000, 0x5cad0000)
 tenured generation   total 768000K, used 626649K [0x5cad0000, 0x8b8d0000, 0x8b8d0000)
   the space 768000K,  81% used [0x5cad0000, 0x82ec66c8, 0x82ec6800, 0x8b8d0000)
 compacting perm gen  total 131072K, used 20K [0x8b8d0000, 0x938d0000, 0x938d0000)
   the space 131072K,   0% used [0x8b8d0000, 0x8b8d5128, 0x8b8d5200, 0x938d0000)
    ro space 8192K,  74% used [0x938d0000, 0x93eca2a8, 0x93eca400, 0x940d0000)
    rw space 12288K,  59% used [0x940d0000, 0x947e7878, 0x947e7a00, 0x94cd0000)
}

log entry using -XX:+PrintGCDateStamps
{Heap before GC invocations=2 (full 1):
 PSYoungGen      total 46080K, used 960K [0x00002aaac3100000, 0x00002aaac6300000, 0x00002aaac6300000)
  eden space 40960K, 0% used [0x00002aaac3100000,0x00002aaac3100000,0x00002aaac5900000)
  from space 5120K, 18% used [0x00002aaac5900000,0x00002aaac59f0000,0x00002aaac5e00000)
  to   space 5120K, 0% used [0x00002aaac5e00000,0x00002aaac5e00000,0x00002aaac6300000)
 PSOldGen        total 210944K, used 0K [0x00002aaab6300000, 0x00002aaac3100000, 0x00002aaac3100000)
  object space 210944K, 0% used [0x00002aaab6300000,0x00002aaab6300000,0x00002aaac3100000)
 PSPermGen       total 21248K, used 5966K [0x00002aaaae300000, 0x00002aaaaf7c0000, 0x00002aaab6300000)
  object space 21248K, 28% used [0x00002aaaae300000,0x00002aaaae8d3840,0x00002aaaaf7c0000)
2012-03-28T07:33:31.630+0000: 0.220: [Full GC 960K->888K(257024K), 0.0134730 secs]
Heap after GC invocations=2 (full 1):
 PSYoungGen      total 46080K, used 0K [0x00002aaac3100000, 0x00002aaac6300000, 0x00002aaac6300000)
  eden space 40960K, 0% used [0x00002aaac3100000,0x00002aaac3100000,0x00002aaac5900000)
  from space 5120K, 0% used [0x00002aaac5900000,0x00002aaac5900000,0x00002aaac5e00000)
  to   space 5120K, 0% used [0x00002aaac5e00000,0x00002aaac5e00000,0x00002aaac6300000)
 PSOldGen        total 210944K, used 888K [0x00002aaab6300000, 0x00002aaac3100000, 0x00002aaac3100000)
  object space 210944K, 0% used [0x00002aaab6300000,0x00002aaab63de008,0x00002aaac3100000)
 PSPermGen       total 21248K, used 5966K [0x00002aaaae300000, 0x00002aaaaf7c0000, 0x00002aaab6300000)
  object space 21248K, 28% used [0x00002aaaae300000,0x00002aaaae8d3840,0x00002aaaaf7c0000)
}
    """

    #print line
    gcre = re.compile('\{Heap before GC.*?' + \
        '(PSYoungGen|def new generation)\s+total (?P<newSize>\d+)K\, used ' + \
            '(?P<newBefore>\d+)K.*?' + \
        'eden space (?P<edenSize>\d+)K\,\s+(?P<edenPrcBefore>\d{1,3})% used.*?' + \
        'from space (?P<fromSize>\d+)K\,\s+(?P<fromPrcBefore>\d{1,3})% used.*?' + \
        'to\s+space (?P<toSize>\d+)K\,\s+(?P<toPrcBefore>\d{1,3})% used.*?' + \
        '(PSOldGen|tenured generation)\s+total (?P<tenuredSize>\d+)K\, used ' + \
            '(?P<tenuredBefore>\d+)K.*?' + \
        '(PSPermGen|compacting perm gen)\s+total (?P<permSize>\d+)K\, used ' + \
            '(?P<permBefore>\d+)K.*?\)\s+' + \
        '(?:(?P<dateGc>\d{4}\-\d{2}\-\d{2}T\d{2}\:\d{2}\:\d{2}\.\d{3}[+-]\d{4})\:?\s*' + \
        '(?P<gctsoffset>\d+\.\d+)\:\s\[GC.*?' + \
        '\,\s+(?P<elapsedGcTime>\d+\.\d+)\ssecs\]\s+){0,1}' + \
        '(?:(?P<dateFullGc>\d{4}\-\d{2}\-\d{2}T\d{2}\:\d{2}\:\d{2}\.\d{3}[+-]\d{4})\:?\s*' + \
        '(?P<fullgctsoffset>\d+\.\d+)\:\s\[Full GC.*?' + \
        '\,\s+(?P<elapsedFullGcTime>\d+\.\d+)\ssecs\]\s+){0,1}' + \
        'Heap after GC.*?' + \
        '(PSYoungGen|def new generation)\s+total (?:\d+)K\, used (?P<newAfter>\d+)K.*?' + \
        'eden space (?:\d+)K\,\s+(?P<edenPrcAfter>\d{1,3})% used.*?' + \
        'from space (?:\d+)K\,\s+(?P<fromPrcAfter>\d{1,3})% used.*?' + \
        'to\s+space (?:\d+)K\,\s+(?P<toPrcAfter>\d{1,3})% used.*?' + \
        '(PSOldGen|tenured generation)\s+total (?:\d+)K\, used ' + \
            '(?P<tenuredAfter>\d+)K.*?' + \
        '(PSPermGen|compacting perm gen)\s+total (?:\d+)K\, used ' + \
            '(?P<permAfter>\d+)K.*?\)' + \
        '.*?\}', re.MULTILINE|re.DOTALL)

    # try matching with the pattern gcre
    match = gcre.match(line)
    if match:
        return match.groupdict()
    else:
        return

        
def drawGraph(elapsedTime, timeStampsFullGc, fullGcIndicators, 
        timeStampsUsed, edenSize, edenUsed, fromSize, fromUsed, toSize, toUsed,
        tenuredSize, tenuredUsed, permSize, permUsed,
        logStartTS, logEndTS, testDuration, output):
    """Draws a graph containing four subplots"""
    # use rc to set defaults
    rc('xtick', labelsize=8)
    rc('ytick', labelsize=8)

    # some additional calculations
    timeInGc = sum(elapsedTime)
    amountFullGc = len(timeStampsFullGc)
    amountGc = (len(timeStampsUsed)-1)/2 - amountFullGc

    figure(1, figsize=(6,8))

    subplots_adjust(hspace=0.8) # adjust space between subplots

    suptitle("GC Analysis (" + logStartTS + " to " + logEndTS + ")")

    ax=subplot(611)
    bar(timeStampsUsed, elapsedTime, width=0.0)
    axis([0, testDuration, 0, 10])     # elapsed up to 10 seconds
    text(0.01, 0.95, 'sec', horizontalalignment='left', verticalalignment='top', 
        transform = ax.transAxes, fontsize=8)
    text(0.99, 0.02, 'min', horizontalalignment='right', verticalalignment='bottom', 
        transform = ax.transAxes, fontsize=8)
    title('GC Time: %i collections, %.2fsec' % (amountGc+amountFullGc, timeInGc),
        x=0, horizontalalignment='left', fontsize=10)

    ax=subplot(612)
    plot(timeStampsUsed, edenSize, 'y')
    fill_between(timeStampsUsed, edenUsed, 0, color='orange')
    axis([0, testDuration, 0, None])   # axis start at 0,0
    text(0.01, 0.95, 'MB', horizontalalignment='left', verticalalignment='top', 
        transform = ax.transAxes, fontsize=8)
    text(0.99, 0.02, 'min', horizontalalignment='right', verticalalignment='bottom', 
        transform = ax.transAxes, fontsize=8)
    title('Eden Space: %i collections' % amountGc,
        x=0, horizontalalignment='left', fontsize=10)

    ax=subplot(613)
    plot(timeStampsUsed, fromSize, 'y')
    fill_between(timeStampsUsed, fromUsed, 0, color='orange')
    axis([0, testDuration, 0, None])   # axis start at 0,0
    text(0.01, 0.95, 'MB', horizontalalignment='left', verticalalignment='top', 
        transform = ax.transAxes, fontsize=8)
    text(0.99, 0.02, 'min', horizontalalignment='right', verticalalignment='bottom', 
        transform = ax.transAxes, fontsize=8)
    title('From Space', x=0, horizontalalignment='left', fontsize=10)

    ax=subplot(614)
    plot(timeStampsUsed, toSize, 'y')
    fill_between(timeStampsUsed, toUsed, 0, color='orange')
    axis([0, testDuration, 0, None])   # axis start at 0,0
    text(0.01, 0.95, 'MB', horizontalalignment='left', verticalalignment='top', 
        transform = ax.transAxes, fontsize=8)
    text(0.99, 0.02, 'min', horizontalalignment='right', verticalalignment='bottom', 
        transform = ax.transAxes, fontsize=8)
    title('To Space', x=0, horizontalalignment='left', fontsize=10)

    ax=subplot(615)
    plot(timeStampsUsed,   tenuredSize, 'y')
    fill_between(timeStampsUsed, tenuredUsed, 0, color='orange')
    plot(timeStampsFullGc, fullGcIndicators, 'ro', markersize=10)
    axis([0, testDuration, 0, None])   # axis start at 0,0
    text(0.01, 0.95, 'MB', horizontalalignment='left', verticalalignment='top', 
        transform = ax.transAxes, fontsize=8)
    text(0.99, 0.02, 'min', horizontalalignment='right', verticalalignment='bottom', 
        transform = ax.transAxes, fontsize=8)
    title('Tenured Space: %i collection(s)' % amountFullGc,
        x=0, horizontalalignment='left', fontsize=10)

    ax=subplot(616)
    plot(timeStampsUsed,   permSize, 'y')
    fill_between(timeStampsUsed, permUsed, 0, color='orange')
    axis([0, testDuration, 0, None])   # axis start at 0,0
    text(0.01, 0.95, 'MB', horizontalalignment='left', verticalalignment='top', 
        transform = ax.transAxes, fontsize=8)
    text(0.99, 0.02, 'min', horizontalalignment='right', verticalalignment='bottom', 
        transform = ax.transAxes, fontsize=8)
    title('Perm Space', x=0, horizontalalignment='left', fontsize=10)

    savefig(output)

    # cleanup
    clf()
    cla()

    
def convertISOToUnixTS(isots):
    """
    Takes a timestamp (supplied from the command line) in ISO format, ie
    yyyy-MM-dd HH:mm:ss and converts it to seconds since the epoch.
    """
    isore = re.compile("(\d{4})-(\d{2})-(\d{2})\s(\d{2}):(\d{2}):(\d{2})")
    mo = isore.match(isots)
    return time.mktime([int(mo.group(1)), int(mo.group(2)), int(mo.group(3)),
        int(mo.group(4)), int(mo.group(5)), int(mo.group(6)), 0, 0, -1])

        
def determin_baseTS(dateGc, tsoffset):
    """
    Takes a timestamp in GC log format, ie
    2012-03-28T07:33:31.630+0000 and converts it to seconds since the epoch.
    """
    tsre = re.compile("(\d{4})\-(\d{2})\-(\d{2})T(\d{2})\:(\d{2})\:(\d{2})\.(\d{3})([+-]\d{4})")
    mo = tsre.match(dateGc)
    return (time.mktime([int(mo.group(1)), int(mo.group(2)), int(mo.group(3)),
        int(mo.group(4)), int(mo.group(5)), int(mo.group(6)), 0, 0, -1]) +
        float(mo.group(7))/float(1000) - float(mo.group(8)) - float(tsoffset) - 
        time.altzone)

        
def baseTimeStamp(logFile):
    """
    Since the timestamps in the gc.log file are probably in seconds since
    server startup, we want to get an indication of the time the first log
    line was written. We do this by getting the ctime of the gc.log file.
    """
    return os.lstat(logFile)[ST_CTIME]

    
def minutesElapsed(currentTS, baseTS):
    """
    Convert the timestamp (in seconds since JVM startup) to mins elapsed
    since first timestamp entry.
    """
    return (currentTS - baseTS) / 60

    
def timeString(ts):
    """
    Return printable version of time represented by seconds since epoch
    """
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ts))

    
def main(config):
    """
    Read the input file line by line, calling out to parse() for each
    line, processing and pushing the tokens into arrays that are passed
    into the drawGraph() method.
    """
    if (config["sliceLogFile"]):
        # convert the timestamps
        if config['baseTS']:
            config["baseTS"] = convertISOToUnixTS(config["baseTS"])
        config["startTime"] = convertISOToUnixTS(config["startTime"])
        config["endTime"] = convertISOToUnixTS(config["endTime"])
    # initialize local variables
    timeStampsFullGc = []
    timeStampsUsed = []
    edenSize = []
    fromSize = []
    toSize = []
    tenuredSize = []
    permSize = []
    edenUsed = [0,]
    fromUsed = [0,]
    toUsed = [0,]
    tenuredUsed = [0,]
    permUsed = [0,]
    elapsedTime = [0,]
    fullGcIndicators = []
    gcStartTS = -1
    gcEndTS = -1
    # read input and parse line by line
    #fin = open(config["input"], 'r')
    fin = config["input"]
    while (True):
        logentry = fin.readline()
        if logentry.startswith('{Heap before GC'):
            while (True):
                nextline = fin.readline()
                if not nextline:
                    logentry = None
                    break
                logentry += nextline
                if (nextline.startswith("}")):
                    break
        else:
            if not logentry:
                break
            else:
                continue
        if not logentry:
            break
        result = parse(logentry)
        if not result:
            #raise(exception('The re-expression did not match %s', logentry))
            pass

        #print result

        # Gc or FullGc or both
        if (result['gctsoffset']):
            tsoffset = float(result['gctsoffset'])
            if not config['baseTS']:
                config['baseTS'] = determin_baseTS(result['dateGc'], result['gctsoffset'])
                #print 'baseTS: %s' % config['baseTS']
                #print 'baseTS: %s' % datetime.datetime.fromtimestamp(config['baseTS'])
        else:
            tsoffset = float(result['fullgctsoffset'])
            if not config['baseTS']:
                config['baseTS'] = determin_baseTS(result['dateFullGc'], result['fullgctsoffset'])
        
        # Set the first timestamp once for the very first record, and keep
        # updating the last timestamp until we run out of lines to read
        if (gcStartTS == -1):
            gcStartTS = tsoffset
        gcEndTS = tsoffset

        # If start and end times are specified, then we should ignore data
        # that are outside the range
        if (config["sliceLogFile"]):
            actualTime = config["baseTS"] - gcStartTS + tsoffset
            if (actualTime < config["startTime"] or actualTime > config["endTime"]):
                continue

        if (len(timeStampsUsed) == 0):
            # workaround because it is difficult to determine the initial size
            # without knowing the configuration; usage is 0
            timeStampsUsed.append(0)
            edenSize.append(int(result['edenSize']) / 1024)
            fromSize.append(int(result['fromSize']) / 1024)
            toSize.append(int(result['toSize']) / 1024)
            tenuredSize.append(int(result['tenuredSize']) / 1024)
            permSize.append(int(result['permSize']) / 1024)

        timeStampsUsed.append(tsoffset)
        elapsed = 0.0
        if (result['elapsedGcTime']):
            elapsed += float(result['elapsedGcTime'])
        if (result['elapsedFullGcTime']):
            elapsed += float(result['elapsedFullGcTime'])
        elapsedTime.append(elapsed)
        timeStampsUsed.append(tsoffset + elapsed)

        # X and Y arrays for GC plot, X will need postprocessing
        if (len(timeStampsUsed) == 0):
            # workaround because it is difficult to determine the initial size
            # without knowing the configuration; usage is 0
            timeStampsUsed.append(0)
            edenSize.append(int(result['edenSize']) / 1024)
            fromSize.append(int(result['fromSize']) / 1024)
            toSize.append(int(result['toSize']) / 1024)
            tenuredSize.append(int(result['tenuredSize']) / 1024)
            permSize.append(int(result['permSize']) / 1024)
        # Before Gc
        edenSize.append(int(result['edenSize']) / 1024)
        edenUsed.append(int(result['edenSize']) * int(result['edenPrcBefore']) / 102400)
        tenuredSize.append(int(result['tenuredSize']) / 1024)
        tenuredUsed.append(int(result['tenuredBefore']) / 1024)
        permSize.append(int(result['permSize']) / 1024)
        permUsed.append(int(result['permBefore']) / 1024)
        # After Gc
        elapsedTime.append(0)
        edenSize.append(int(result['edenSize']) / 1024)
        edenUsed.append(int(result['edenSize']) * int(result['edenPrcAfter']) / 102400)
        tenuredSize.append(int(result['tenuredSize']) / 1024)
        tenuredUsed.append(int(result['tenuredAfter']) / 1024)
        permSize.append(int(result['permSize']) / 1024)
        permUsed.append(int(result['permAfter']) / 1024)
        # exchange From-To after each Gc run
        if (len(fromUsed) == 0 or fromUsed[-1] == 0):
            fromUsed.append(int(result['fromSize']) *
                int(result['toPrcBefore']) / 102400)
            fromUsed.append(int(result['fromSize']) *
                int(result['fromPrcAfter']) / 102400)
            toUsed.append(int(result['toSize']) * 
                int(result['fromPrcBefore']) / 102400)
            toUsed.append(int(result['toSize']) *
                int(result['toPrcAfter']) / 102400)
        else:
            fromUsed.append(int(result['fromSize']) *
                int(result['fromPrcBefore']) / 102400)
            fromUsed.append(int(result['fromSize']) *
                int(result['toPrcAfter']) / 102400)
            toUsed.append(int(result['toSize']) * 
                int(result['toPrcBefore']) / 102400)
            toUsed.append(int(result['toSize']) *
                int(result['fromPrcAfter']) / 102400)
        fromSize.append(int(result['fromSize']) / 1024)
        fromSize.append(int(result['fromSize']) / 1024)
        toSize.append(int(result['toSize']) / 1024)
        toSize.append(int(result['toSize']) / 1024)

        # Full Gc
        if (result['elapsedFullGcTime']):
            timeStampsFullGc.append(tsoffset)
            fullGcIndicators.append(0)

    fin.close()
    # Convert log start and end time stamps to printable format
    if (config["sliceLogFile"]):
        logStartTS = timeString(config["startTime"])
        logEndTS = timeString(config["endTime"])
        # start the plot at the given start time (teststart - JVMstart)
        testStartTime = config["startTime"] - config["baseTS"]
        testDuration  = (config["endTime"] - config["startTime"]) / 60
    else:
        logStartTS = timeString(config["baseTS"])
        logEndTS = timeString(config["baseTS"] + gcEndTS - gcStartTS)
        testStartTime = timeStampsUsed[0]
        testDuration = (timeStampsUsed[-1] - timeStampsUsed[0]) / 60
    # convert timestamps from seconds since JVM startup to minutes elapsed
    # since first timestamp entry
    for i in range(len(timeStampsFullGc)):
        timeStampsFullGc[i] = minutesElapsed(timeStampsFullGc[i], testStartTime)
    for i in range(len(timeStampsUsed)):
        timeStampsUsed[i] = minutesElapsed(timeStampsUsed[i], testStartTime)

    # Call function to graph results
    drawGraph(elapsedTime, timeStampsFullGc, fullGcIndicators, 
        timeStampsUsed, edenSize, edenUsed, fromSize, fromUsed, toSize, toUsed,
        tenuredSize, tenuredUsed, permSize, permUsed,
        logStartTS, logEndTS, testDuration, config['output'])

    return 0


def usage():
    """
    Prints the script's usage guide.
    """
    print "Usage: plot_gc.py input output [server-time-start] [time-start] [time-end]"
    print "input = path to gc.log file"
    print "output = path to gc.png file"
    print "server-time-start = date in yyyy-MM-dd HH:mm:ss format"
    print "time-start = date in yyyy-MM-dd HH:mm:ss format"
    print "time-end = date in yyyy-MM-dd HH:mm:ss format"
    sys.exit(-1)


if __name__ == "__main__":
    #print sys.argv
    if len(sys.argv) not in [3,5,6]:
        usage()

    with tarfile.open(sys.argv[1], 'r') as tar:
        # tgz file contains multiple jvm-gc.log files which we have to analyze
        for tarinfo in tar:
            if tarinfo.isreg():
                # check for suitable logfiles
                filename = re.match(r'^\.\/(.*)\/logs\/jvm-gc.log$', tarinfo.name)
                if filename:
                    fi = tar.extractfile(tarinfo.name)
                    outputfile = filename.group(1) + '-gc.png'
    
                config = {
                    #"input":  sys.argv[1],
                    "input":  fi,
                    "output": os.path.join(sys.argv[2], outputfile)
                }
                # optional start and end times provided
                if (len(sys.argv) == 6):
                    config["sliceLogFile"] = True
                    #in many cases the auto basetime does not work because the file
                    #must be collected from the server (pls look up server start from logfile)
                    config["baseTS"]    = sys.argv[3]
                    config["startTime"] = sys.argv[4]
                    config["endTime"]   = sys.argv[5]
                elif (len(sys.argv) == 5):
                    config["sliceLogFile"] = True
                    #in many cases the auto basetime does not work because the file
                    #must be collected from the server (pls look up server start from logfile)
                    config["baseTS"]    = None
                    config["startTime"] = sys.argv[3]
                    config["endTime"]   = sys.argv[4]
                else:
                    config["sliceLogFile"] = False
                    # The base time is the ctime for the log file
                    config["baseTS"]    = baseTimeStamp(sys.argv[1])
                    config["startTime"] = 0
                    config["endTime"]   = 0

                main(config)
 