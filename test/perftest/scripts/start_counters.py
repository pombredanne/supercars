#!/usr/bin/env python

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


def execute(ssh, script, targetdir, duration):
    '''execute the script'''
    ssh.exec_command('cd %s; nohup ./%s %s' % (targetdir, script, duration))


def usage():
    """
    Prints the script's usage guide.
    """
    print "Usage: collect_logs.py environment testrun"
    print "environment = Name of the environment defined in the environments.ini file"
    print "duration = duration for the counters to run [in ms]"


def start(environments, duration):
    """Start counters on specified environments"""

    for environment in environments:
        # load environment settings from INI file
        config = ConfigParser.ConfigParser()
        config.read('environments.ini')
        host = config.get(environment, 'host', 0)
        usr = config.get(environment, 'usr', 0)
        pwd = config.get(environment, 'pwd', 0)
        zipfolder = config.get(environment, 'zipfolder', 0)

        # prepare ssh connection
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(
            paramiko.AutoAddPolicy())
        ssh.connect(host, username=usr, password=pwd)

        upload(ssh, 'scripts/counters.sh', zipfolder)

        set_userrights(ssh, 'counters.sh', zipfolder)

        # start counters
        execute(ssh, 'counters.sh', zipfolder, duration)

        ssh.close()

    return True


def main(argv=None):
    if argv is None:
        argv = sys.argv
    if len(argv) != 3:
        usage()
        return False

    environments = [x.strip() for x in sys.argv[1].split(',')]
    duration = argv[2]
    return start(environments, duration)


if __name__ == "__main__":
    sys.exit(main())
