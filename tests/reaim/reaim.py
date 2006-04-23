# Needs autoconf & automake & libtool to be installed. Ewwwwwwwwwwwwwwwwwwwwww
import test
from autotest_utils import *

class reaim(test.test):
	version = 1

	# http://prdownloads.sourceforge.net/re-aim-7/osdl-aim-7.0.1.13.tar.gz
	def setup(self, tarball = 'osdl-aim-7.0.1.13.tar.gz'):
		tarball = unmap_url(self.bindir, tarball, self.tmpdir)
		extract_tarball_to_dir(tarball, self.srcdir)
		os.chdir(self.srcdir)

		system('./bootstrap')
		system('./configure')
		system('make')
		
	def execute(self, workfile = 'workfile.short', 
			start = '1', end = '10', increment = '2',
			testdir = None):
		if not testdir:
			testdir = self.tmpdir
		args = '-f ' + ' '.join(workfile.short,start,end,increment)
		system(self.srcdir + './reaim ' + args)
