#!/bin/bash
#
#  Simple Idle power measurement test, stress vm subsystem
#

#
# Number of samples
#
SAMPLES=100
#
# Interval between samples in seconds
#
SAMPLE_INTERVAL=5
#
# Default for tests is to wait SETTLE_DURATION before kicking
# of a new test.
#
SETTLE_DURATION=30

#
# Duration of stress test, plus a bit of slop
#
DURATION=$(((SAMPLES + 1) * $SAMPLE_INTERVAL))

CPUS=$(cat /proc/cpuinfo  | grep processor | wc -l)

#
# Meter configs need setting
#
if [ -z $METER_ADDR ]; then
	echo "METER_ADDR not configured!"
	exit 1
fi
if [ -z $METER_PORT ]; then
	echo "METER_PORT not configured!"
	exit 1
fi
if [ -z $METER_TAGPORT ]; then
	echo "METER_TAGPORT not configured!"
	exit 1
fi
if [ -z $SAMPLES_LOG ]; then
	echo "SAMPLES_LOG not configured!"
	exit 1
fi
if [ -z $STATISTICS_LOG ]; then
	echo "STATISTICS_LOG not configured!"
	exit 1
fi

#
#  Tools for gathering data and analysis
#
if [ -z $LOGMETER ]; then
	echo "LOGMETER not configured!"
	exit 1
fi
if [ ! -x $LOGMETER ]; then
	echo "Cannot find LOGMETER at $LOGMETER"
	exit 1
fi

if [ -z $STATSTOOL ]; then
	echo "STATSTOOL not configured!"
	exit 1
fi
if [ ! -x $STATSTOOL ]; then
	echo "Cannot find STATSTOOL at $STATSTOOL"
	exit 1
fi

#
# Flush dirty pages and drop caches
#
sync; sleep 1
sync; sleep 1
(echo 1 | sudo tee /proc/sys/vm/drop_caches) > /dev/null
(echo 2 | sudo tee /proc/sys/vm/drop_caches) > /dev/null
(echo 3 | sudo tee /proc/sys/vm/drop_caches) > /dev/null
sync; sleep 1
#
# Wait a little to settle
#
sleep ${SETTLE_DURATION}

#
# Kick off stress test
#
stress -t $DURATION --vm $CPUS > /dev/null 2>&1 &

#
# Gather samples
#
rm -f $SAMPLES_LOG
$LOGMETER --addr=$METER_ADDR --port=$METER_PORT --tagport=$METER_TAGPORT \
          --measure=c --acdc=AC \
	  --interval=$SAMPLE_INTERVAL --samples=$SAMPLES \
	  --out=$SAMPLES_LOG
#
# And kill off stress
#
killall -9 stress

#
# Compute stats, scale by 1000 because we are using a power clamp
#
echo "info:test:test-vm"
$STATSTOOL -S -T -X 1000 -a $SAMPLES_LOG
