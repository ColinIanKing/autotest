#!/usr/bin/env python
#

from autotest.client                    import utils
import re

class WiFi():

    # __init__
    #
    def __init__(s):
        pass
        s.__exists = None
        s.__vendor = None
        s.__model  = None

        s.__caps = {
            'Intel' : {
                '6205' : {
                    'sta'    : 'true',        # station mode

                    '24ghz'  : 'true',        # 2.4GHz band
                    '11b'    : 'true',
                    '11g'    : 'true',

                    '5ghz'   : 'true',        # 5GHz band
                    '11a'    : 'true',

                    '11n'    : 'true',        # 802.11n (both bands)
                    'ht40'   : 'true',        # HT40
                    'sgi40'  : 'true',        # Short GI in HT40
                }
            },

            'Atheros' : {
                'AR9285' : {
                    'sta'    : 'true',        # station mode

                    '24ghz'  : 'true',        # 2.4GHz band
                    '11b'    : 'true',
                    '11g'    : 'true',

                    '5ghz'   : 'false',       # 5GHz band
                    '11a'    : 'false',

                    '11n'    : 'true',        # 802.11n (both bands)
                    'ht40'   : 'true',        # HT40
                    'sgi40'  : 'true',        # Short GI in HT40
                }
            },

            'Broadcom' : {
                'BCM43224' : {
                    'sta'    : 'true',        # station mode

                    '24ghz'  : 'true',        # 2.4GHz band
                    '11b'    : 'true',
                    '11g'    : 'true',

                    '5ghz'   : 'true',        # 5GHz band
                    '11a'    : 'true',

                    '11n'    : 'true',        # 802.11n (both bands)
                    'ht40'   : 'false',       # HT40
                    'sgi40'  : 'true',        # Short GI in HT40
                }
            }
        }

    def __run_cmd(s, cmd, ignore_status=False):
        return utils.system_output(cmd + ' 2>&1', retain_output=True, ignore_status=ignore_status).strip()

    # exists
    #
    def exists(s):
        '''
        Does this system have WiFi installed on it?
        '''
        if s.__exists is None:
            s.__exists = False
            pci = s.__run_cmd("lspci")
            for line in pci.split('\n'):
                lh, rh = line.rsplit(':', 1)
                if 'Network controller' in lh:
                    s.__exists = True
                    if 'Intel' in rh:
                        s.__vendor = 'Intel'
                        l = rh.replace('Intel Corporation ', '')
                        l = l.replace('Centrino Advanced-N ', '')
                        m = re.search('(\d+) \(rev \d+\)', l)
                        if m:
                            s.__model = m.group(1)

                    elif 'Atheros' in rh:
                        s.__vendor = 'Atheros'
                        l = rh.replace('Atheros Communications Inc. ', '')
                        m = re.search('(AR\d+) .*', l)
                        if m:
                            s.__model = m.group(1)

                    elif 'Broadcom' in rh:
                        s.__vendor = 'Broadcom'
                        l = rh.replace('Broadcom Corporation ', '')
                        m = re.search('(BCM\d+) .*', l)
                        if m:
                            s.__model = m.group(1)

        return s.__exists

    # vendor
    #
    @property
    def vendor(s):
        '''
        The WiFi device vendor name.
        '''
        if s.__vendor is None:
            s.exists()
        return s.__vendor

    # model
    #
    @property
    def model(s):
        '''
        The WiFi device model number.
        '''
        if s.__model is None:
            s.exists()
        return s.__model

    # caps
    #
    @property
    def caps(s):
        '''
        Return the list of capabilities for this vendor/model.
        '''
        retval = None
        if s.exists():
            try:
                retval = s.__caps[s.__vendor][s.__model]
            except KeyError:
                retval = {
                    'sta'    : 'true',        # station mode

                    '24ghz'  : 'true',        # 2.4GHz band
                    '11b'    : 'true',
                    '11g'    : 'true',

                    '5ghz'   : 'true',        # 5GHz band
                    '11a'    : 'true',

                    '11n'    : 'true',        # 802.11n (both bands)
                    'ht40'   : 'true',        # HT40
                    'sgi40'  : 'true',        # Short GI in HT40
                }
        return retval


# vi:set ts=4 sw=4 expandtab syntax=python:
