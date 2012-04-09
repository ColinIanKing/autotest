import os
from autotest_lib.client.bin import test, utils

class qrt(test.test):
    version = 1

    def initialize(self):
        self.job.require_gcc()

    def setup(self, tarball = 'qrt.tar.bz2'):
        tarball = utils.unmap_url(self.bindir, tarball, self.tmpdir)
        utils.extract_tarball_to_dir(tarball, self.srcdir)

    def run_once(self, args = '', user = 'root'):
        scripts = os.path.join(self.srcdir, 'scripts')
        os.chdir(scripts)

        cmd = 'python ./test-kernel-hardening.py -v'
        self.results = utils.system_output(cmd, retain_output=True)

        cmd = 'test-kernel-aslr-collisions.py -v'
        self.results = utils.system_output(cmd, retain_output=True)

        cmd = 'python ./test-kernel-panic.py -v'
        self.results = utils.system_output(cmd, retain_output=True)

        cmd = 'python ./test-kernel-security.py -v'
        self.results = utils.system_output(cmd, retain_output=True)


# vi:set ts=4 sw=4 expandtab:
