#!/usr/bin/python
"""
Program that parses autotest metrics results and prints them to stdout,
so that the jenkins measurement-plots plugin can parse them.

Copyright Canonical, Inc 2012
"""
from sys                             import argv, exit
from getopt                          import getopt, GetoptError
import os
import json
from datetime                        import datetime, date
#from string                          import replace

#clean_MB_s{perf}=463.92
#compile_MB_s{perf}=47.70
#delete_tree_secs{perf}=2.19
#initial_create_MB_s{perf}=47.48
#new_create_MB_s{perf}=31.13
#patch_MB_s{perf}=16.71
#read_compiled_tree_MB_s{perf}=47.43
#read_tree_MB_s{perf}=32.48
#stat_compiled_tree_secs{perf}=1.92
#stat_tree_secs{perf}=1.77

def main(path, testname):

    # under here is a "results" directory
    # The files we care about are:
    # results/default/dbench/keyval
    # results/default/dbench/results/keyval

    meta = {}
    metrics = {}
    results = {}

    metaFileList = []
    metaFileList.append(os.path.join(path, "results/default/", testname, "keyval"))
    metricFileList = []
    metricFileList.append(os.path.join(path, "results/default/", testname, "results/keyval"))

    meta['results_processed'] = datetime.utcnow().strftime("%A, %d. %B %Y %H:%M UTC")
    meta['testname'] = testname
    for filenm in metaFileList:
        fd = open(filenm, "r")
        lines = fd.readlines()
        for line in lines:
            p =  line.strip().split('=')
            if len(p) != 2:
                continue
            meta[p[0]] = p[1]

    for filenm in metricFileList:
        fd = open(filenm, "r")
        lines = fd.readlines()
        for line in lines:
            p =  line.strip().split('=')
            if len(p) != 2:
                continue
            metrics[p[0]] = p[1]

    results['meta'] = meta
    results['metrics'] = metrics
    print json.dumps(results, sort_keys=True, indent=4)

    return

def usage():
    print "                                                                                             \n",
    print "    %s                                                                                       \n" % argv[0],
    print "        reads result files from an autotest benchmark, and outputs the information as        \n",
    print "        json data.                                                                           \n",
    print "                                                                                             \n",
    print "    Usage:                                                                                   \n",
    print "        %s --testname <testname> [options] <path-to-results>                                 \n" % argv[0],
    print "                                                                                             \n",
    print "    Options:                                                                                 \n",
    print "        --help           Prints this text.                                                   \n",
    print "                                                                                             \n",
    print "        --testname=<test_name>           The name of the test that was run (required).       \n",
    print "                                                                                             \n",
    print "        --path=<results_path>            The path to the results files (required).           \n",
    print "                                                                                             \n",
    print "    Examples:                                                                                \n",
    print "        %s --testname=dbench --path=/var/lib/jenkins/jobs/dbench-test/workspace/dbench       \n" % argv[0],

if __name__ == "__main__":
    # process command line
    try:
        optsShort = ''
        optsLong  = ['help', 'testname=', 'path=']
        opts, args = getopt(argv[1:], optsShort, optsLong)
        testname = None
        path = None

        for opt, val in opts:
            if (opt == '--help'):
                usage()
            elif opt in ('--testname'):
                testname = val.strip()
            elif opt in ('--path'):
                path = val.strip()

    except GetoptError:
        usage()

    if testname == None or path == None:
        usage()
        exit()

    main(path, testname)
