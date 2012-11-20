#!/usr/bin/env python

import sys
import os
import tarfile
import shutil


def archive_plots(source_folder, target):
    '''archive all plots in source_folder'''
    t = tarfile.open(name=target, mode='w:gz')
    t.add(source_folder)  # os.path.basename(source))
    t.close()

    shutil.rmtree(source_folder)


def usage():
    """
    Prints the script's usage guide.
    """
    print "Usage: analyze-logs.py testrun"
    print "testrun = foldername of the testrun e.g. 12032712"


def main(argv=None):
    if argv is None:
        argv = sys.argv
    if len(argv) != 2:
        usage()
        return False
    else:
        savedPath = os.getcwd()
        os.chdir('testruns/%s/' % argv[1])  # cd into the folder
        archive_plots('_plots', 'plots-%s.tar.gz' % argv[1])
        shutil.move('plots-%s.tar.gz' % argv[1], 'plots-%s.tgz' % argv[1])
        os.chdir(savedPath)  # cd back to the original folder
        return True

if __name__ == "__main__":
    sys.exit(main())
