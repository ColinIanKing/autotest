#!/usr/bin/python2

"""Tests for autoserv_parser."""

import sys
import unittest

try:
    import autotest.common as common
except ImportError:
    import common
from autotest.server import autoserv_parser


class autoserv_parser_test(unittest.TestCase):

    def setUp(self):
        self.orig_sys_argv = sys.argv

    def tearDown(self):
        sys.argv = self.orig_sys_argv

    def _get_parser(self):
        # We resort to this vile hack because autoserv_parser is bad
        # enough to instantiate itself and replace its own class definition
        # with its instance at module import time.  Disgusting.
        return autoserv_parser.autoserv_parser.__class__()

    def test_control_file_args(self):
        sys.argv = [None, '--args', '-y  -z foo --hello', 'controlfile']
        parser = self._get_parser()
        parser.parse_args()
        self.assertEqual(['controlfile', '-y', '-z', 'foo', '--hello'],
                         parser.args)


if __name__ == '__main__':
    unittest.main()
