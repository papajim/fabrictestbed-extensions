#!/usr/bin/env python3
# MIT License
#
# Copyright (c) 2020 FABRIC Testbed
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following nditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# Author: Paul Ruth (pruth@renci.org)
from __future__ import annotations
from fabrictestbed.slice_editor import Flags
from tabulate import tabulate
from ipaddress import IPv4Address
import json

import logging


from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from fabrictestbed_extensions.fablib.slice import Slice
    from fabrictestbed_extensions.fablib.node import Node
    from fabrictestbed_extensions.fablib.network_service import NetworkService
    from fabrictestbed_extensions.fablib.component import Component

from fim.user.interface import Interface as FimInterface


class Interface:

    def __init__(self, component: Component = None, fim_interface: FimInterface = None):
        """
        Constructor. Sets keyword arguments as instance fields.

        :param component: the component to set on this interface
        :type component: Component
        :param fim_interface: the FABRIC information model interface to set on this fablib interface
        :type fim_interface: FimInterface
        """
        super().__init__()
        self.fim_interface = fim_interface
        self.component = component
        self.network = None
        
    def get_fablib_manager(self):
        return self.get_slice().get_fablib_manager()

    def __str__(self):
        """
        Creates a tabulated string describing the properties of the interface.

        Intended for printing interface information.

        :return: Tabulated string of interface information
        :rtype: String
        """
        if self.get_network():
            network_name = self.get_network().get_name()
        else:
            network_name = None

        table = [   [ "Name", self.get_name() ],
                    [ "Network", network_name ],
                    [ "Bandwidth", self.get_bandwidth() ],
                    [ "VLAN", self.get_vlan() ],
                    [ "MAC", self.get_mac() ],
                    [ "Physical Device", self.get_physical_os_interface_name() ],
                    [ "Device", self.get_os_interface() ],
                    ]

        return tabulate(table)

    def toJson(self):
        """
        Returns the interface attributes as a json string

        :return: slice attributes as json string
        :rtype: str
        """
        return json.dumps(self.toDict(), indent=4)

    def toDict(self):
        """
        Returns the interface attributes as a dictionary

        :return: slice attributes as dictionary
        :rtype: dict
        """
        if self.get_network():
            logging.info(f"Getting results from get network name thread for iface {self.get_name()} ")
            network_name = self.get_network().get_name()
        else:
            network_name = None

        if self.get_node():
            logging.info(f"Getting results from get node name thread for iface {self.get_name()} ")
            node_name = self.get_node().get_name()
        else:
            node_name = None

        return {  "Name": self.get_name(),
                  "Node": node_name,
                  "Network": network_name,
                  "Bandwidth": self.get_bandwidth(),
                  "VLAN": self.get_vlan(),
                  "MAC": self.get_mac(),
                  "Physical Device": self.get_physical_os_interface_name(),
                  "Device": self.get_os_interface(),
                 }



    def show(self, fields=None, output=None, quiet=False, colors=False):
        """
        Show a table containing the current interface attributes.

        There are several output options: "text", "pandas", and "json" that determine the format of the
        output that is returned and (optionally) displayed/printed.

        output:  'text': string formatted with tabular
                  'pandas': pandas dataframe
                  'json': string in json format

        fields: json output will include all available fields.

        Example: fields=['Name','MAC']

        :param output: output format
        :type output: str
        :param fields: list of fields to show
        :type fields: List[str]
        :param quiet: True to specify printing/display
        :type quiet: bool
        :param colors: True to specify state colors for pandas output
        :type colors: bool
        :return: table in format specified by output parameter
        :rtype: Object
        """

        data = self.toDict()
    
        fields = ["Name", "Node", "Network", "Bandwidth", "VLAN",
                "MAC", "Device"
                 ]
    
        table = self.get_fablib_manager().show_table(data, 
                        fields=fields,
                        title='Interface', 
                        output=output, 
                        quiet=quiet)
            
            
        return table

    def set_auto_config(self):
        fim_iface = self.get_fim_interface()
        fim_iface.flags = Flags(auto_config=True)
        #fim_iface.labels = Labels.update(fim_iface.labels, ipv4.... )

        #labels = Labels()
        #labels.instance_parent = host_name
        #self.get_fim_node().set_properties(labels=labels)

        #if_labels = Labels.update(if_labels, ipv4=str(next(ips)), ipv4_subnet=str(network))
        # if_labels = Labels.update(if_labels, vlan="200", ipv4=str(next(ips)))
        #fim_iface.set_properties(labels=if_labels)

    def unset_auto_config(self):
        fim_iface = self.get_fim_interface()
        fim_iface.flags = Flags(auto_config=False)


    def get_device_name(self) -> str:
        """
         Gets a name of the device name on the node

         If the interface requires a FABRIC VLAN tag, the interface name returned
         will be the VLAN tagged interface name.

         :return: OS interface name
         :rtype: String
         """
        try:
            # logging.debug(f"iface: {self}")
            os_iface = self.get_physical_os_interface_name()
            vlan = self.get_vlan()

            if vlan is not None:
                os_iface = f"{os_iface}.{vlan}"
        except:
            os_iface = None

        return os_iface

    def get_os_interface(self) -> str:
        """
        Deprecated: see interface.get_device_name()

        Gets a name of the interface the operating system uses for this
        FABLib interface.

        If the interface requires a FABRIC VLAN tag, the interface name retruned
        will be the VLAN tagged.

        :return: OS interface name
        :rtype: String
        """
        try:
            #logging.debug(f"iface: {self}")
            os_iface = self.get_physical_os_interface_name()
            vlan = self.get_vlan()

            if vlan is not None:
                os_iface = f"{os_iface}.{vlan}"
        except:
            os_iface = None

        return os_iface

    def get_mac(self) -> str:
        """
        Gets the MAC address of the interface.

        :return: MAC address
        :rtype: String
        """
        try:
            #os_iface = self.get_physical_os_interface()
            #mac = os_iface['mac']
            mac = self.get_fim_interface().get_property(pname="label_allocations").mac
        except:
            mac = None

        return mac

    def get_os_dev(self):
        """
        Gets json output of 'ip addr list' for the interface.

        :return: device description
        :rtype: Dict
        """

        ip_addr_list_json = self.get_node().ip_addr_list(output='json')

        mac = self.get_mac()
        for dev in ip_addr_list_json:
            if str(dev['address'].upper()) == str(mac.upper()):
                return dev

        return None

    def get_physical_os_interface(self):
        """
        Not intended for API use
        """

        if self.get_network() is None:
            return None

        network_name = self.get_network().get_name()
        node_name = self.get_node().get_name()

        try:
            return self.get_slice().get_interface_map()[network_name][node_name]
        except:
            return None

    def get_physical_os_interface_name(self) -> str:
        """
        Gets a name of the physical interface the operating system uses for this
        FABLib interface.

        If the interface requires a FABRIC VLAN tag, the base interface name
        will be returned (i.e. not the VLAN tagged interface)

        :return: physical OS interface name
        :rtype: String
        """
        try:
            return self.get_os_dev()['ifname']
        except:
            return None

    def config_vlan_iface(self):
        """
        Not intended for API use
        """
        if self.get_vlan() is not None:
            self.get_node().add_vlan_os_interface(os_iface=self.get_physical_os_interface_name(),
                                                  vlan=self.get_vlan(), interface=self)

    def set_ip(self, ip=None, cidr=None, mtu=None):
        """
        Depricated
        """
        if cidr: cidr=str(cidr)
        if mtu: mtu=str(mtu)

        self.get_node().set_ip_os_interface(os_iface=self.get_physical_os_interface_name(),
                                            vlan=self.get_vlan(),
                                            ip=ip, cidr=cidr, mtu=mtu)

    def ip_addr_add(self, addr, subnet):
        """
        Add an IP address to the interface in the node.

        :param addr: IP address
        :type addr: IPv4Address or IPv6Address
        :param subnet: subnet
        :type subnet: IPv4Network or IPv4Network
        """
        self.get_node().ip_addr_add(addr, subnet, self)

    def ip_addr_del(self, addr, subnet):
        """
        Delete an IP address to the interface in the node.

        :param addr: IP address
        :type addr: IPv4Address or IPv6Address
        :param subnet: subnet
        :type subnet: IPv4Network or IPv4Network
        """
        self.get_node().ip_addr_del(addr, subnet, self)

    def ip_link_up(self):
        """
        Bring up the link on the interface.

        """
        if self.get_network() == None:
            return
        
        self.get_node().ip_link_up(None, self)

    def ip_link_down(self):
        """
        Bring down the link on the interface.

        """
        self.get_node().ip_link_down(None, self)

    def ip_link_toggle(self):
        """
        Toggle the dev down then up.

        """
        self.get_node().ip_link_down(None, self)
        self.get_node().ip_link_up(None, self)

    def set_vlan(self, vlan: Any = None):
        """
        Set the VLAN on the FABRIC request.

        :param addr: vlan
        :type addr: String or int
        """
        if vlan:
            vlan = str(vlan)

        if_labels = self.get_fim_interface().get_property(pname="labels")
        if_labels.vlan = str(vlan)
        self.get_fim_interface().set_properties(labels=if_labels)

    def get_fim_interface(self) -> FimInterface:
        """
        Not recommended for most users.

        Gets the node's FABRIC Information Model (fim) object. This method
        is used to access data at a lower level than FABlib.

        :return: the FABRIC model node
        :rtype: fim interface
        """
        return self.fim_interface

    def get_bandwidth(self) -> str:
        """
        Gets the bandwidth of an interface. Basic NICs claim 0 bandwidth but
        are 100 Gbps shared by all Basic NICs on the host.

        :return: bandwith
        :rtype: String
        """
        if self.get_component().get_model() == 'NIC_Basic':
            return 100
        else:
            return self.get_fim_interface().capacities.bw

    def get_vlan(self) -> str:
        """
        Gets the FABRIC VLAN of an interface.

        :return: VLAN
        :rtype: String
        """
        try:
            vlan = self.get_fim_interface().get_property(pname="labels").vlan
        except:
            vlan = None
        return vlan

    def get_reservation_id(self) -> str or None:
        try:
            #TODO THIS DOESNT WORK.
            #print(f"{self.get_fim_interface()}")
            return self.get_fim_interface().get_property(pname='reservation_info').reservation_id
        except:
            return None

    def get_reservation_state(self) -> str or None:
        """
        Gets the reservation state

        :return: VLAN
        :rtype: String
        """
        try:
            return self.get_fim_interface().get_property(pname='reservation_info').reservation_state
        except:
            return None

    def get_error_message(self) -> str:
        """
        Gets the error messages

        :return: error
        :rtype: String
        """
        try:
            return self.get_fim_interface().get_property(pname='reservation_info').error_message
        except:
            return ""

    def get_name(self) -> str:
        """
        Gets the name of this interface.

        :return: the name of this interface
        :rtype: String
        """
        return self.get_fim_interface().name

    def get_component(self) -> Component:
        """
        Gets the component attached to this interface.

        :return: the component on this interface
        :rtype: Component
        """
        return self.component

    def get_model(self) -> str:
        """
        Gets the component model type on this interface's component.

        :return: the model of this interface's component
        :rtype: str
        """
        return self.get_component().get_model()

    def get_site(self) -> str:
        """
        Gets the site this interface's component is on.

        :return: the site this interface is on
        :rtype: str
        """
        return self.get_component().get_site()

    def get_slice(self) -> Slice:
        """
        Gets the FABLIB slice this interface's node is attached to.

        :return: the slice this interface is attached to
        :rtype: Slice
        """
        return self.get_node().get_slice()

    def get_node(self) -> Node:
        """
        Gets the node this interface's component is on.

        :return: the node this interface is attached to
        :rtype: Node
        """
        return self.get_component().get_node()

    def get_network(self) -> NetworkService:
        """
        Gets the network this interface is on.

        :return: the network service this interface is on
        :rtype: NetworkService
        """
        if self.network is not None:
            #print(f"hasattr(self, 'network'): {hasattr(self, 'network')}, {self.network.get_name()}")
            return self.network
        else:
            for net in self.get_slice().get_networks():
                if net.has_interface(self):
                    self.network = net
                    #print(f"return found network, {self.network.get_name()}")
                    return self.network

        #print(f"hasattr(self, 'network'): {hasattr(self, 'network')}, None")
        return None

    
    # fablib.Interface.get_ip_link()
    def get_ip_link(self):
        """
        Gets the ip link info for this interface.

        :return ip link info
        :rtype: str
        """
        try:
            stdout, stderr = self.get_node().execute('ip -j link list', quiet=True)

            links = json.loads(stdout)

            dev = self.get_os_interface()
            if dev == None:
                return links

            for link in links:
                if link['ifname'] == dev:
                    return link
            return None    
        except Exception as e:
            print(f"Exception: {e}")

    # fablib.Interface.get_ip_addr()
    def get_ip_addr(self):
        """
        Gets the ip addr info for this interface.

        :return ip addr info
        :rtype: str
        """
        try:
            stdout, stderr = self.get_node().execute('ip -j addr list', quiet=True)

            addrs = json.loads(stdout)

            dev = self.get_os_interface()
            #print(f"dev: {dev}")            

            if dev == None:
                return addrs

            for addr in addrs:
                if addr['ifname'] == dev:
                    return addr['addr_info'][0]['local']

            return None    
        except Exception as e:
            print(f"Exception: {e}")


    # fablib.Interface.get_ip_addr()
    def get_ips(self, family=None):
        """
        Gets a list of ips assigned to this interface.

        :return list of ips
        :rtype: list[str]
        """
        return_ips = []
        try:
            dev = self.get_os_interface()

            ip_addr = self.get_ip_addr()

            #print(f"{ip_addr}")

            for addr_info in ip_addr['addr_info']:
                if family == None:
                    return_ips.append(addr_info['local'])
                else:
                    if addr_info['family'] == family:
                        return_ips.append(addr_info['local'])        
        except Exception as e:
            print(f"Exception: {e}")

        return return_ips