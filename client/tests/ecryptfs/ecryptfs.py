import os
from autotest_lib.client.bin import test, utils

class ecryptfs(test.test):
    version = 1

    def initialize(self):
        self.job.require_gcc()

    def setup(self, tarball = 'ecryptfs.tar.bz2'):
        tarball = utils.unmap_url(self.bindir, tarball, self.tmpdir)
        utils.extract_tarball_to_dir(tarball, self.srcdir)

        os.chdir(self.srcdir)
        utils.system('autoreconf -ivf')
        utils.system('intltoolize -c -f')
        utils.configure('--enable-tests --disable-pywrap')
        utils.make()

    def run_once(self, args = '', user = 'root'):
        print("run_once: Enter")

        for dir in ['/mnt/upper', '/mnt/lower', '/mnt/image']:
            if not os.path.isdir(dir):
                os.makedirs(dir)

        FS_TYPES = ['ext2', 'ext3', 'ext4', 'xfs', 'btrfs']

        os.chdir(self.srcdir)
        for fs_type in FS_TYPES:
            for test_type in ['destructive', 'safe']:
                cmd = 'tests/run_tests.sh -K -c %s -b 1000000 -D /mnt/image -l /mnt/lower -u /mnt/upper -f %s' % (test_type, fs_type)
                self.results = utils.system_output(cmd, retain_output=True)

        print("run_once: Leave")

# vi:set ts=4 sw=4 expandtab:
