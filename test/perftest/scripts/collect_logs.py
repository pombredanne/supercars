#!/usr/bin/env python
"""
(c) Mark Fink, 2008 - 2013
This script is released under the MIT License
Warranty in any form is excluded
"""

import os
import re
import sys
import ConfigParser

import paramiko
from scp.scp import SCPClient


def testrun_folder(targetdir, testrun):
    '''make sure testrun folder is available'''
    if not os.path.exists(os.path.join(targetdir, testrun)):
        os.makedirs(os.path.join(targetdir, testrun))


def zip_files(ssh, remotedir, pattern, archive):
    '''zip all the files on remote which follow a given pattern'''
    stdin, stdout, sterr = ssh.exec_command('cd %s; find -L . -regex "%s" ' % (remotedir, pattern) + 
        '-type f -print | xargs tar cf - | gzip -c > %s' % archive)
    
    channel = stdout.channel.recv_exit_status()  # exec_command is non-blocking, wait for exit status

    
def collect_file(ssh, archive, targetdir):
    '''get a file from remote'''
    scp = SCPClient(ssh.get_transport())
    scp.get(archive, targetdir)
    
    
def remove_files(ssh, remotedir, pattern):
    '''remove all files on remote'''
    stdin, stdout, sterr = ssh.exec_command('cd %s; find -L . -regex "%s" ' % (remotedir, pattern) + 
        '-type f -print | xargs rm ')

    channel = stdout.channel.recv_exit_status()  # exec_command is non-blocking, wait for exit status

    
def oscounters(ssh, environment, logdir, remotedir, testrun, targetdir):
    ''' zip the OS counters on remote and store them with the other testrun files '''
    # get the pid(s)
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command('cd %s; ls *.pid' % os.path.join(remotedir, '_os'))
    try:
        while ssh_stdout:
            pid = re.match('^(\d{8})\.pid$', ssh_stdout.next()).group(1) # for all pids
            zip_files(ssh, '%s/_os/' % remotedir, '^.*\.txt\.%s$' % pid, '%s/%s-oscounters-%s.tgz' % (remotedir, environment, pid))
            testrun_folder(targetdir, pid)
            collect_file(ssh, '%s/%s-oscounters-%s.tgz' % (remotedir, environment, pid), os.path.join(targetdir, pid))
            # remove the files on remote
            remove_files(ssh, remotedir, './%s-oscounters-%s.tgz' % (environment, pid))
            remove_files(ssh, '%s/_os/' % remotedir, '^.*\.txt\.%s$' % pid)
            remove_files(ssh, '%s/_os/' % remotedir, '^.*%s.pid$' % pid)
    except StopIteration:
        pass

def appcounters(ssh, environment, logdir, remotedir, testrun, targetdir):
    ''' zip the OS counters on remote and store them with the other testrun files '''
    # get the pid(s)
    ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command('cd %s; ls *.pid' % os.path.join(remotedir, '_app'))
    try:
        while ssh_stdout:
            pid = re.match('^(\d{8})\.pid$', ssh_stdout.next()).group(1) # for all pids
            zip_files(ssh, '%s/_app/' % remotedir, '^.*\.txt\.%s$' % pid, '%s/%s-appcounters-%s.tgz' % (remotedir, environment, pid))
            testrun_folder(targetdir, pid)
            collect_file(ssh, '%s/%s-appcounters-%s.tgz' % (remotedir, environment, pid), os.path.join(targetdir, pid))
            # remove the files on remote
            remove_files(ssh, remotedir, './%s-appcounters-%s.tgz' % (environment, pid))
            remove_files(ssh, '%s/_app/' % remotedir, '^.*\.txt\.%s$' % pid)
            remove_files(ssh, '%s/_app/' % remotedir, '^.*%s.pid$' % pid)
    except StopIteration:
        pass

        
def traces(ssh, environment, logdir, remotedir, testrun, targetdir):
    ''' zip the physmon traces on remote and store them with the other testrun files '''
    zip_files(ssh, logdir, '.*\/.*-trace\.log\.?\d*', '%s/%s-traces-%s.tgz' % (remotedir, environment, testrun))
    testrun_folder(targetdir, testrun)
    collect_file(ssh, '%s/%s-traces-%s.tgz' % (remotedir, environment, testrun), os.path.join(targetdir, testrun))
    # remove the files on remote
    remove_files(ssh, remotedir, './%s-traces-%s.tgz' % (environment, testrun))       
        

def gclogs(ssh, environment, logdir, remotedir, testrun, targetdir):
    ''' zip the GC logfiles on remote and store them with the other testrun files '''
    zip_files(ssh, logdir, '.*\/jvm-gc.log', '%s/%s-gclogs-%s.tgz' % (remotedir, environment, testrun))
    testrun_folder(targetdir, testrun)
    collect_file(ssh, '%s/%s-gclogs-%s.tgz' % (remotedir, environment, testrun), os.path.join(targetdir, testrun))
    # remove the files on remote
    #remove_files(ssh, remotedir, './%s-gclogs-%s.tgz' % (environment, testrun))


def applogs(ssh, environment, logdir, remotedir, testrun, targetdir):
    '''collect application logfiles relevant for testrun'''
    # exclude trace.log files
    postfix = '20' + testrun[0:2] + '\-' + testrun[2:4] + '\-' + testrun[4:6]
    stdin, stdout, sterr = ssh.exec_command('cd %s; find -L . -regex ".*\/.*\.log(\.%s)?" ' % 
        (logdir, postfix) + 
        "-type f -print0 | grep -Zzv trace.log | xargs -0 tar cf - | gzip -c > %s/%s-applogs-%s.tgz"
        % (remotedir, environment, testrun))

    channel = stdout.channel.recv_exit_status()  # exec_command is non-blocking, wait for exit status
    testrun_folder(targetdir, testrun)
    collect_file(ssh, '%s/%s-applogs-%s.tgz' % (remotedir, environment, testrun), os.path.join(targetdir, testrun))
    # remove the files on remote
    remove_files(ssh, remotedir, './%s-applogs-%s.tgz' % (environment, testrun))


def usage():
    """
    Prints the script's usage guide.
    """
    print 'Usage: collect_logs.py testrun "env1, env2,..." "oscounters, applogs, gclogs, traces"'
    print "testrun = Name of the test execution e.g. 12032713"
    print "environments = Name of the environment defined in the environments.ini file"
    print "logtypes = List types of logfiles to collect"

    
def collect(environments, logtypes, testrun, targetdir):
    """Collect specified logtypes from environments"""
    
    for environment in environments:
        # load environment settings from INI file
        config = ConfigParser.ConfigParser()
        config.read('environments.ini')
        host = config.get(environment, 'host', 0)
        usr = config.get(environment, 'usr', 0)
        pwd = config.get(environment, 'pwd', 0)
        remotedir = config.get(environment, 'zipfolder', 0)
        logdir = config.get(environment, 'logdir', 0)
        
        # prepare ssh connection
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(
            paramiko.AutoAddPolicy())
        ssh.connect(host, username=usr, password=pwd)

        # collect the different logtypes for this environment
        map(lambda logtype: globals()[logtype](ssh, environment, logdir, remotedir, testrun, targetdir), logtypes)
        
        ssh.close()
    
    return True
    
    
        
def main(argv=None):
    if argv is None:
        argv = sys.argv
    if len(argv) != 4:
        usage()
        return False
    testrun = sys.argv[1]
    environments = [x.strip() for x in sys.argv[2].split(',')]
    logtypes = [x.strip() for x in sys.argv[3].split(',')]
    return collect(environments, logtypes, testrun, './testruns/')


if __name__ == "__main__":
    sys.exit(main())

