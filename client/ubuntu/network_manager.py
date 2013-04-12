#!/usr/bin/env python
#

from os                                 import getenv, path
from argparse                           import ArgumentParser, RawDescriptionHelpFormatter
from logging                            import error, debug, basicConfig, INFO, DEBUG, getLogger
import dbus
from uuid                               import uuid4
import socket
import fcntl
import struct

# NoSuchConnectionError
#
class NoSuchConnectionError(Exception):
    """
    """
    def __init__(s, connection_id):
        s.__connection_id = connection_id

    def __str__(s):
        return '%s: A connection by that name was not found' % s.__connection_id

    @property
    def connection_id(s):
        return s.__connection_id

# NetworkManager
#
# http://projects.gnome.org/NetworkManager/developers/api/09/spec.html
# http://projects.gnome.org/NetworkManager/developers/api/09/ref-settings.html
#
class NetworkManager():
    '''
    A helper class to make working with network manager via dbus a little
    easier.
    '''
    # __init__
    #
    def __init__(s):
        s.bus = dbus.SystemBus()
        p = s.bus.get_object("org.freedesktop.NetworkManager", "/org/freedesktop/NetworkManager")
        s.network_manager = dbus.Interface(p, "org.freedesktop.NetworkManager")

        p = s.bus.get_object("org.freedesktop.NetworkManager", "/org/freedesktop/NetworkManager/Settings")
        s.network_manager_settings = dbus.Interface(p, "org.freedesktop.NetworkManager.Settings")

        s.name_of_devtype = {
            1 : 'Ethernet',
            2 : 'WiFi',
            5 : 'Bluetooth',
            6 : 'OLPC',
            7 : 'WiMAX',
            8 : 'Modem',
            9 : 'InfiniBand',
           10 : 'Bond',
           11 : 'VLAN',
           12 : 'ADSL',
        }

        s.name_of_state = {
           10 : 'Unmanaged',
           20 : 'Unavailable',
           30 : 'Disconnected',
           40 : 'Prepare',
           50 : 'Config',
           60 : 'Need Auth',
           70 : 'IP Config',
           80 : 'IP Check',
           90 : 'Secondaries',
          100 : 'Activated',
          110 : 'Deactivating',
          120 : 'Failed',
        }

    # connections
    #
    @property
    def connections(s):
        return s.network_manager_settings.ListConnections()

    # get_connection_settings
    #
    def get_connection_settings(s, ptso):
        '''
        ptso - Path to settings object.
        '''
        o = s.get_object(ptso)
        return o.GetSettings(), o

    # get_object
    #
    def get_object(s, pto):
        '''
        pto - Path to object
        '''
        return s.bus.get_object('org.freedesktop.NetworkManager', pto)

    # delete_wifi_connection
    #
    def delete_wifi_connection(s, setting_id):
        connection = s.find_wifi_connection(setting_id)
        if connection is not None:
            connection.Delete()

    # create_wifi_connection
    #
    def create_wifi_connection(s, setting):

        dd = setting
        if type(setting) is dict:
            # Convert it to a dbus.Dictionary
            #
            dd = dbus.Dictionary()
            for k in setting:
                dd[k] = dbus.Dictionary()
                for k2 in setting[k]:
                    dd[k][k2] = setting[k][k2]

            dd['connection']['uuid'] = str(uuid4())

            if '802-11-wireless' in setting:
                dd['802-11-wireless']['ssid'] = setting['802-11-wireless']['ssid']

        s.network_manager_settings.AddConnection(dd)

    # activate_wifi_connection
    #
    def activate_wifi_connection(s, setting_id):
        connection = s.find_wifi_connection(setting_id)
        if connection is not None:
            target_device = s.network_manager.GetDeviceByIpIface('wlan0')
            s.network_manager.ActivateConnection(connection, target_device, '/')

    # find_wifi_connection
    #
    def find_wifi_connection(s, setting_id):
        retval = None
        for x in s.connections:
            settings, connection = s.get_connection_settings(x)

            try:
                wifi = settings['802-11-wireless']
                if settings['connection']['id'] == setting_id:
                    retval = connection
                    break

            except KeyError:
                pass

        if retval is None:
            raise NoSuchConnectionError(setting_id)

        return retval

    # active_wifi_device
    #
    def active_wifi_device(s):
        retval = None
        devices = s.network_manager.GetDevices()
        for d in devices:
            dev_proxy = s.bus.get_object("org.freedesktop.NetworkManager", d)
            prop_iface = dbus.Interface(dev_proxy, "org.freedesktop.DBus.Properties")

            # Get the device's current state and interface name
            state = prop_iface.Get("org.freedesktop.NetworkManager.Device", "State")
            name  = prop_iface.Get("org.freedesktop.NetworkManager.Device", "Interface")
            kind  = prop_iface.Get("org.freedesktop.NetworkManager.Device", "DeviceType")

            if state == 100 and kind == 2:
                retval = name
                break
        return str(retval)

    # active_wifi_device_ip
    #
    def active_wifi_device_ip(s):
        retval = None

        wifi_dev = s.active_wifi_device()
        if wifi_dev:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            info = fcntl.ioctl(sock.fileno(), 0x8915, struct.pack('256s', wifi_dev[:15]))
            retval = socket.inet_ntoa(info[20:24])

        return retval

# vi:set ts=4 sw=4 expandtab syntax=python:
