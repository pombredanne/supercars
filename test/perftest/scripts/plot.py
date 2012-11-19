#!/usr/bin/env python

from collections import OrderedDict
import sys
import os
import tarfile
import logging
from datetime import datetime, timedelta
import re

from plot_sar import main as sar
from plot_vmstat import main as vmstat
from plot_top import main as top
from plot_gc import main as gc
from plot_physmon import main as physmon

#import profile


def usage():
    """
    Prints the script's usage guide.
    """
    print 'Usage: plot.py testrun start end "env1, env2,..." "traces, vmstat, top, sar, gc"'
    print "testrun = Name of the test execution e.g. 12032713"
    print "start = date in yyyy-MM-dd HH:mm:ss format"
    print "end = date in yyyy-MM-dd HH:mm:ss format"
    print "environments = Name of the environment defined in the environments.ini file"
    print "plottypes = List types of plots to create"
    print "plotfolder = location where to store the plots"


def plot(testrun, start, end, environments, plottypes, testrundir, plotfolder):
    """Create specified plots for environments"""

    logging.basicConfig(
        filename=os.path.join(testrundir, 'plot_error.log'),
        level=logging.INFO,
        format='%(asctime)s %(message)s'
    )
    
    logger = logging.getLogger('logparser')

    suffix = os.path.basename(sys.argv[2]).split('.', 1)[0].split('-', 2)[2]

    for environment in environments:

        # config here
        config = {}
        config['host'] = environment
        config['output'] = plotfolder
        config['startTime'] = datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
        config['endTime'] =  datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
        
        if 'sar' in plottypes:
            with tarfile.open(os.path.join(testrundir, '%s-oscounters-%s.tgz' % (environment, testrun)), 'r') as tar:
                logger.info('Processing sar in %s-oscounters-%s.tgz' % (environment, testrun))
                fi = tar.extractfile('./sar.txt.%s' % testrun)
                config['input'] = fi
                try:
                    sar(config)
                except:
                    logger.error(sys.exc_info())
            
        if 'vmstat' in plottypes:
            with tarfile.open(os.path.join(testrundir, '%s-oscounters-%s.tgz' % (environment, testrun)), 'r') as tar:
                logger.info('Processing vmstat in %s-oscounters-%s.tgz' % (environment, testrun))
                fi = tar.extractfile('./vmstat.txt.%s' % testrun)
                config['input'] = fi
                try:
                    vmstat(config)
                except:
                    logger.error(sys.exc_info())
            
        if 'top' in plottypes:
            with tarfile.open(os.path.join(testrundir, '%s-oscounters-%s.tgz' % (environment, testrun)), 'r') as tar:
                logger.info('Processing top in %s-oscounters-%s.tgz' % (environment, testrun))
                fi = tar.extractfile('./top.txt.%s' % testrun)
                config['input'] = fi
                try:
                    top(config)
                except:
                    logger.error(sys.exc_info())

        if 'gc' in plottypes:
            with tarfile.open(os.path.join(testrundir, '%s-gclogs-%s.tgz' % (environment, testrun)), 'r') as tar:
               logger.info('Processing %s-gclogs-%s.tgz' % (environment, testrun))
               for tarinfo in tar:
                    if tarinfo.isreg():
                        # check for suitable logfiles
                        filename = re.match(r'^\.\/(.*)\/jvm-gc.log$', tarinfo.name)
                        if filename:
                            fi = tar.extractfile(tarinfo.name)
                            outputfile = filename.group(1) + '-gc.png'
                            config['input'] = fi
                            config['output'] = os.path.join(plotfolder, environment + '_' + outputfile)
                            config['sliceLogFile'] = True
                            config['startTime'] = start
                            config['endTime'] = end
                            config["baseTS"] = None
                            try:
                                gc(config)
                            except:
                                logger.error(sys.exc_info())

        if 'traces' in plottypes:
            with tarfile.open(os.path.join(testrundir, '%s-traces-%s.tgz' % (environment, testrun)), 'r:gz') as tar:
                logger.info('Processing %s-traces-%s.tgz' % (environment, testrun))
                files = []
                for tarinfo in tar:
                    if tarinfo.isreg():
                        # check for suitable logfiles
                        if re.match(r'^.*-trace\.log\.?\d*$', tarinfo.name):
                            files.append(tar.extractfile(tarinfo.name))
                config['input'] = files
                # define steps, order is important for stacked area graph
                config['steps'] = OrderedDict()
                config['steps']['enqueued_to_phmsns']   = ('start', 'measurements')
                config['steps']['dequeued_from_phmsns'] = ('end', 'measurements')
                config['steps']['before_import']       = ('start', 'import')
                config['steps']['after_import']        = ('end', 'import')
                config['steps']['enqueued_to_amq']     = ('start', 'assigned measurement')
                config['steps']['dequeued_from_amq']   = ('end', 'assigned measurement')
                config['steps']['before_check']        = ('start', 'check')
                config['steps']['after_check']         = ('end', 'check')
                config['steps']['enqueued_to_phmalr']   = ('start', 'alarm')
                config['steps']['dequeued_from_phmalr'] = ('end', 'alarm')
                config['steps']['before_mail']         = ('start', 'mail')
                config['steps']['after_mail']          = ('end', 'mail')        
                try:
                    #profile.run('physmon(config)')
                    physmon(config)
                except:
                    logger.error(sys.exc_info())
                            
    return True

    
def main(argv=None):
    if argv is None:
        argv = sys.argv
    if len(argv) != 8:
        usage()
        return False

    environments = [x.strip() for x in sys.argv[4].split(',')]
    plottypes = [x.strip() for x in sys.argv[5].split(',')]
    return plot(sys.argv[1], sys.argv[2], sys.argv[3], environments, plottypes, sys.argv[6], sys.argv[7])


if __name__ == "__main__":
    sys.exit(main())

