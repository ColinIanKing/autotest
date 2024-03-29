#!/usr/bin/python2
"""Reexecute parser in scenario and store the result at specified tag.
"""

import optparse
import sys
from os import path
try:
    import autotest.common as common
except ImportError:
    import common
from autotest.tko.parsers.test import scenario_base

usage = 'usage: %prog [options] scenario_dirpath parser_result_tag'
parser = optparse.OptionParser(usage=usage)


def main():
    (options, args) = parser.parse_args()
    if len(args) < 2:
        parser.print_help()
        sys.exit(1)

    scenario_dirpath = path.normpath(args[0])
    parser_result_tag = args[1]

    if not path.exists(scenario_dirpath) or not path.isdir(scenario_dirpath):
        print 'Invalid scenarios_dirpath:', scenario_dirpath
        parser.print_help()
        sys.exit(1)

    tempdir, results_dirpath = scenario_base.load_results_dir(scenario_dirpath)
    harness = scenario_base.new_parser_harness(results_dirpath)
    try:
        parser_result = harness.execute()
    except Exception, e:
        parser_result = e
    scenario_base.store_parser_result(
        scenario_dirpath, parser_result, parser_result_tag)
    tempdir.clean()


if __name__ == '__main__':
    main()
