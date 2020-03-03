"""
Canonical specific code catch-all
"""

import os, utils

def setup_proxy():
    # Hacky way to use proxy settings, ideally this should be done on deployment stage
    #
    print "Setup the http/https proxy"
    proxysets = [{'addr': 'squid.internal', 'desc': 'Running in the Canonical CI environment'},
              {'addr': '91.189.89.216', 'desc': 'Running in the Canonical enablement environment'},
              {'addr': '10.245.64.1', 'desc': 'Running in the Canonical enablement environment'}]
    for proxy in proxysets:
        cmd = 'nc -w 2 ' + proxy['addr'] + ' 3128'
        try:
            utils.system_output(cmd, retain_output=False)
            print proxy['desc']
            os.environ['http_proxy'] = 'http://' + proxy['addr'] + ':3128'
            os.environ['https_proxy'] = 'http://' + proxy['addr'] + ':3128'
            break
        except:
            pass
