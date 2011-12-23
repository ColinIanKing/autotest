#!/usr/bin/python
"""
Program that parses the autotest results and generates JUnit test results in XML format.

Based on scan_results.py, which is @copyright: Red Hat 2008-2009
"""
from sys                             import argv, stdout, exit
import os
from datetime                        import datetime, date
#from traceback                       import format_exc
#from string                          import maketrans
from xml.sax.saxutils                import escape
#import uuid

import JUnit_api as api


def parse_results(text):
    """
    Parse text containing Autotest results.

    @return: A list of result 4-tuples.
    """
    result_list = []
    start_time_list = []
    info_list = []

    lines = text.splitlines()
    for line in lines:
        line = line.strip()
        parts = line.split("\t")

        # Found a START line -- get start time
        if (line.startswith("START") and len(parts) >= 5 and
            parts[3].startswith("timestamp")):
            start_time = float(parts[3].split("=")[1])
            start_time_list.append(start_time)
            info_list.append("")

        # Found an END line -- get end time, name and status
        elif (line.startswith("END") and len(parts) >= 5 and
              parts[3].startswith("timestamp")):
            end_time = float(parts[3].split("=")[1])
            start_time = start_time_list.pop()
            info = info_list.pop()
            test_name = parts[2]
            test_status = parts[0].split()[1]
            # Remove "kvm." prefix
            if test_name.startswith("kvm."):
                test_name = test_name[4:]
            result_list.append((test_name, test_status,
                                int(end_time - start_time), info))

        # Found a FAIL/ERROR/GOOD line -- get failure/success info
        elif (len(parts) >= 6 and parts[3].startswith("timestamp") and
              parts[4].startswith("localtime")):
            info_list[-1] = parts[5]

    return result_list


def main(basedir, resfiles):
    result_lists = []
    name_width = 40

    try:
        hn = open(os.path.join(basedir, "sysinfo/hostname")).read()
    except:
        hn = "localhost"


    testsuites = api.testsuites()
    ts = api.testsuite(name="Autotest tests")
    properties = api.propertiesType()
    ts.hostname = hn
    ts.timestamp = date.isoformat(date.today())

    # collect some existing report file contents as properties
    to_collect = [
        "cmdline","cpuinfo","df","gcc_--version",
        "installed_packages","interrupts",
        "ld_--version","lspci_-vvn","meminfo",
        "modules","mount","partitions",
        "proc_mounts","slabinfo","uname",
        "uptime","version"
        ]

    for propitem in to_collect:
        try:
            contents = open(os.path.join(basedir, "sysinfo", propitem)).read()
        except:
            contents = "Unable to open the file %s" % os.path.join(basedir, "sysinfo", propitem)
        tp = api.propertyType(propitem, contents)
        properties.add_property(tp)
    
    # Parse and add individual results
    for resfile in resfiles:
        try:
            text = open(resfile).read()
        except IOError, e:
            if e.errno == 21: # Directory
                continue
            else:
                continue

        # status is all we care about
        if os.path.basename(resfile) == "status":
            results = parse_results(text)
            result_lists.append((resfile, results))
            name_width = max([name_width] + [len(r[0]) for r in results])

    testcases = []
    tests = 0
    failures = 0
    errors = 0
    time = 0
    for resfile, results in result_lists:
        if len(results):
            for r in results:

                # handle test case xml generation
                tname = r[0]
                # first, see if this is the overall test result
                if tname.strip() == '----':
                    testsuite_result = r[1]
                    testsuite_time = r[2]
                    continue

                # otherwise, it's a test case
                tc = api.testcaseType()
                tc.name = tname
                tc.classname = 'autotest'
                tc.time = int(r[2])
                tests = tests + 1
                if r[1] == 'GOOD':
                # success, we append the testcase without an error or fail
                    pass
                # Count NA as fails, disable them if you don't want them
                elif r[1] == 'TEST_NA':
                    failures = failures+1
                    tcfailure = api.failureType(message='Test %s is Not Applicable' % tname, type_ = 'Failure', valueOf_ = "%s" % r[3])
                    tc.failure = tcfailure
                elif r[1] == 'ERROR':
                    failures = failures+1
                    tcfailure = api.failureType(message='Test %s has failed' % tname, type_ = 'Failure', valueOf_ = "%s" % r[3])
                    tc.failure = tcfailure
                else:
                    # we don't know what this is
                    errors = errors+1
                    tcerror = api.errorType(message='Unexpected value for result in test result for test %s' % tname, type_ = 'Logparse', valueOf_ = "result=%s" % r[1])
                    tc.error = tcerror
                testcases.append(tc)
        else:
            # no results to be found
            tc = api.testcaseType()
            tc.name = 'Logfilter'
            tc.classname = 'logfilter'
            tc.time = 0
            tcerror = api.errorType(message='LOGFILTER: No test cases found while parsing log', type_ = 'Logparse', valueOf_ = 'nothing to show')
            tc.error = tcerror
            testcases.append(tc)

        #if testsuite_result == "GOOD":
        #    if failures or error:
        #        raise RuntimeError("LOGFILTER internal error - Overall test results parsed as good, but test errors found")
        for tc in testcases:
            ts.add_testcase(tc)
        ts.failures = failures
        ts.errors = errors
        ts.time = testsuite_time
        ts.tests = tests
        ts.set_properties(properties)
        # TODO find and include stdout and stderr
        testsuites.add_testsuite(ts)
        testsuites.export(stdout, 0)

if __name__ == "__main__":
    import glob

    basedir =  glob.glob("../../results/default")
    resfiles = glob.glob(os.path.join(basedir, "/status*"))
    if len(argv) > 1:
        if argv[1] == "-h" or argv[1] == "--help":
            print "Usage: %s [result files basedir]" % argv[0]
            exit(0)
        basedir = os.path.dirname(argv[1])
        #resfiles = glob.glob(os.path.join(sys.argv[1:], "/status*"))
    main(basedir, argv[1:])
