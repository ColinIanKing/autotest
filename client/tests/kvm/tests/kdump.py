import logging, time
from autotest_lib.client.common_lib import error
import kvm_subprocess, kvm_test_utils, kvm_utils


def run_kdump(test, params, env):
    """
    KVM reboot test:
    1) Log into a guest
    2) Check and enable the kdump
    3) For each vcpu, trigger a crash and check the vmcore

    @param test: kvm test object
    @param params: Dictionary with the test parameters
    @param env: Dictionary with test environment.
    """
    vm = kvm_test_utils.get_living_vm(env, params.get("main_vm"))
    timeout = float(params.get("login_timeout", 240))
    crash_timeout = float(params.get("crash_timeout", 360))
    session = kvm_test_utils.wait_for_login(vm, 0, timeout, 0, 2)
    def_kernel_param_cmd = ("grubby --update-kernel=`grubby --default-kernel`"
                            " --args=crashkernel=128M@64M")
    kernel_param_cmd = params.get("kernel_param_cmd", def_kernel_param_cmd)
    def_kdump_enable_cmd = "chkconfig kdump on && service kdump start"
    kdump_enable_cmd = params.get("kdump_enable_cmd", def_kdump_enable_cmd)

    def crash_test(vcpu):
        """
        Trigger a crash dump through sysrq-trigger

        @param vcpu: vcpu which is used to trigger a crash
        """
        session = kvm_test_utils.wait_for_login(vm, 0, timeout, 0, 2)
        session.get_command_status("rm -rf /var/crash/*")

        logging.info("Triggering crash on vcpu %d ...", vcpu)
        crash_cmd = "taskset -c %d echo c > /proc/sysrq-trigger" % vcpu
        session.sendline(crash_cmd)

        if not kvm_utils.wait_for(lambda: not session.is_responsive(), 240, 0,
                                  1):
            raise error.TestFail("Could not trigger crash on vcpu %d" % vcpu)

        logging.info("Waiting for kernel crash dump to complete")
        session = kvm_test_utils.wait_for_login(vm, 0, crash_timeout, 0, 2)

        logging.info("Probing vmcore file...")
        s = session.get_command_status("ls -R /var/crash | grep vmcore")
        if s != 0:
            raise error.TestFail("Could not find the generated vmcore file")
        else:
            logging.info("Found vmcore.")

        session.get_command_status("rm -rf /var/crash/*")

    try:
        logging.info("Checking the existence of crash kernel...")
        prob_cmd = "grep -q 1 /sys/kernel/kexec_crash_loaded"
        s = session.get_command_status(prob_cmd)
        if s != 0:
            logging.info("Crash kernel is not loaded. Trying to load it")
            # We need to setup the kernel params
            s, o = session.get_command_status_output(kernel_param_cmd)
            if s != 0:
                raise error.TestFail("Could not add crashkernel params to"
                                     "kernel")
            session = kvm_test_utils.reboot(vm, session, timeout=timeout);

        logging.info("Enabling kdump service...")
        # the initrd may be rebuilt here so we need to wait a little more
        s, o = session.get_command_status_output(kdump_enable_cmd, timeout=120)
        if s != 0:
            raise error.TestFail("Could not enable kdump service: %s" % o)

        nvcpu = int(params.get("smp", 1))
        for i in range (nvcpu):
            crash_test(i)

    finally:
        session.close()
