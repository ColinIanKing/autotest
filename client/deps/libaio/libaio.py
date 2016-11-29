#!/usr/bin/python

import os
from autotest.client import utils

version = 2


def setup(tarball, topdir):
    srcdir = os.path.join(topdir, 'src')
    utils.extract_tarball_to_dir(tarball, srcdir)
    os.chdir(srcdir)
    utils.make()
    utils.make('prefix=%s install' % topdir)
    os.chdir(topdir)


# old source was
# http://www.kernel.org/pub/linux/kernel/people/bcrl/aio/libaio-0.3.92.tar.bz2
# http://ftp.debian.org/debian/pool/main/liba/libaio/libaio_0.3.106.orig.tar.gz
# now grabbing from upstream project on github
# https://github.com/autotest/autotest/tree/master/client/deps/libaio

pwd = os.getcwd()
tarball = os.path.join(pwd, 'libaio_0.3.110-1.tar.gz')
utils.update_version(pwd + '/src', False, version, setup, tarball, pwd)
