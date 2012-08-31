import os
from autotest_lib.client.bin import test, utils

class power_consumption(test.test):
    version = 1

    def initialize(self):
        self.job.require_gcc()

    def setup(self, instrument_lib_tarball = 'instrument-lib.tar.bz2'):
        instrument_lib_tarball = utils.unmap_url(self.bindir, instrument_lib_tarball, self.tmpdir)
        utils.extract_tarball_to_dir(instrument_lib_tarball, self.srcdir)

	#
	# make the tools
	#
	statstool = os.path.join(self.srcdir, 'statstool')
	os.chdir(statstool)
	utils.make()
	
    def run_once(self, test_name):
        if test_name == 'setup':
            return

        os.chdir(self.srcdir)
	#
	#  Meter and tools configuration
	#
	os.putenv('METER_ADDR', '192.168.0.2')
	os.putenv('METER_PORT', '3490')
	os.putenv('METER_TAGPORT', '9999')
	os.putenv('LOGMETER', os.path.join(self.srcdir, 'logmeter'))
	os.putenv('STATSTOOL', os.path.join(os.path.join(self.srcdir, 'statstool'), 'statstool'))
	os.putenv('SAMPLES_LOG', os.path.join(os.path.join(self.tmpdir, 'samples.log')))
	os.putenv('STATISTICS_LOG', os.path.join(os.path.join(self.tmpdir, 'statistics.log')))

	script = os.path.join(os.path.join(self.bindir, 'power_consumption_tests'), test_name)
        self.results = utils.system_output(script, retain_output=True)

# vi:set ts=4 sw=4 expandtab:
