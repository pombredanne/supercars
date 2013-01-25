#!/usr/bin/env python
"""
(c) Mark Fink, 2008 - 2013
This script is released under the MIT License
Warranty in any form is excluded
"""

import datetime
import os
import re
import sys
import ConfigParser

import paramiko
from scp.scp import SCPClient


def upload(ssh, script, targetdir):
    '''upload a file to remote'''
    scp = SCPClient(ssh.get_transport())
    scp.put(script, targetdir)
    
    
def set_userrights(ssh, script, targetdir):
    '''set the user rights on remote'''
    ssh.exec_command('cd %s; chmod a+x %s' % (targetdir, script))


def execute(ssh, script, targetdir, duration, arguments):
    '''execute the script'''
    ssh.exec_command('cd %s; nohup ./%s %s %s' % (targetdir, script, duration, ' '.join(arguments)))


def usage():
    """
    Prints the script's usage guide.
    """
    print "Usage: start_counters.py environment testrun duration <argument-names>"
    print "environment = Name of the environment defined in the environments.ini file"
    print "duration = duration for the counters to run [in ms]"
    print "... more script specific argument-names that are read from ini file"


def start(environments, script, duration, argnames):
    """Start counters on specified environments"""

    for environment in environments:
        # load environment settings from INI file
        config = ConfigParser.ConfigParser()
        config.read('environments.ini')
        host = config.get(environment, 'host', 0)
        usr = config.get(environment, 'usr', 0)
        pwd = config.get(environment, 'pwd', 0)
        zipfolder = config.get(environment, 'zipfolder', 0)
        arguments = [config.get(environment, x, 0) for x in argnames]

        # prepare ssh connection
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(
            paramiko.AutoAddPolicy())
        ssh.connect(host, username=usr, password=pwd)

        upload(ssh, 'scripts/%s' % script, zipfolder)
        
        set_userrights(ssh, script, zipfolder)

        # start counters
        execute(ssh, script, zipfolder, duration, arguments)
        
        ssh.close()
    
    return True

    
def main(argv=None):
    if argv is None:
        argv = sys.argv
    if len(argv) < 4:
        usage()
        return False

    environments = [x.strip() for x in sys.argv[1].split(',')]
    script = argv[2]
    duration = argv[3]
    argnames = argv[4:]

    return start(environments, script, duration, argnames)


if __name__ == "__main__":
    sys.exit(main())

