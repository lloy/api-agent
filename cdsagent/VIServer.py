import os
import os.path
import time
import socket
import sys
import string
import ssl
import base64
from pysphere import VIServer
from pysphere import VIException, VIApiException, FaultTypes

#Server Control
class ESXi_Server:
    server_ip    = ''
    user_name    = ''
    password     = ''
    connect_flag = False
    server       = None
    #vm_list      = []

    #def __init__(self):
    
    #Use the given args to connect the esxi server you want
    #@ip[string]: ESXi server's IP address
    #@name[string]: the username used to login the ESXi server
    #@pwd[string]: the password used to login the ESXi server
    def connect_server(self, ip, name, pwd):
        self.server_ip = ip
        self.user_name = name
        self.password  = pwd
        self.server = VIServer()
        self.server.connect(self.server_ip, self.user_name, self.password)
        self.connect_flag = self.server.is_connected()
        if self.connect_flag:
            return True
        return False

    #To get all the definition registered vms from the connected server
    #@param[string]: can be set as ALL, POWER_ON, POWER_OFF, SUSPENDED
    #According to the param, returns a list of VM Paths. You might also filter by datacenter,
    #cluster, or resource pool by providing their name or MORs. 
    #if  cluster is set, datacenter is ignored, and if resource pool is set
    #both, datacenter and cluster are ignored.
    def get_registered_vms(self, param, status=None, datacenter=None, cluster=None, 
                           resource_pool=None):
        if param not in ['ALL', 'POWER_ON', 'POWER_OFF', 'SUSPENDED']:
            print "Get VMs error: param can only be set as ALL, POWER_ON, POWER_OFF, or SUSPENDED."
            return None
        if self.connect_flag == False:
            print "Get VMs error: Server not connected."
            return None
        if param == 'ALL':
            return self.server.get_registered_vms(datacenter, cluster, resource_pool)
        elif param == 'POWER_ON':
            return self.server.get_registered_vms(datacenter, cluster, resource_pool, status='poweredOn')
        elif param == 'POWER_OFF':
            return self.server.get_registered_vms(datacenter, cluster, resource_pool, status='poweredOff')
        elif param == 'SUSPENDED':
            return self.server.get_registered_vms(datacenter, cluster, resource_pool, status='suspended')
        else:
            return None
    
    #Disconnect to the Server
    def disconnect(self):
        if self.connect_flag == True:
            self.server = self.server.disconnect()
            self.connect_flag == False

    #To keep session alive 
    def keep_session_alive(self):
        assert self.server.keep_session_alive()

    #To get the server type
    def get_server_type(self):
        return self.server.get_server_type()

    #To get performance manager
    def get_performance_manager(self):
        return self.server.get_performance_manager()

    #To get the all the server's hosts
    def get_all_hosts(self):
        """
        Returns a dictionary of the existing hosts keys are their names
        and values their ManagedObjectReference object.
        """
        return self.server.get_hosts()
    
    #To get all datastores
    def get_all_datastores(self):
        """
        Returns a dictionary of the existing datastores. Keys are
        ManagedObjectReference and values datastore names.
        """
        return self.server.get_datastores()

    #To get all clusters
    def get_all_clusters(self):
        """
        Returns a dictionary of the existing clusters. Keys are their 
        ManagedObjectReference objects and values their names.
        """
        return self.server.get_clusters()

    #To get all datacenters
    def get_all_datacenters(self):
        """
        Returns a dictionary of the existing datacenters. keys are their
        ManagedObjectReference objects and values their names.
        """
        return self.server.get_datacenters()

    #To get all resource pools
    def get_all_resource_pools(self):
        """
        Returns a dictionary of the existing ResourcePools. keys are their
        ManagedObjectReference objects and values their full path names.
        """
        return self.server.get_resource_pools()
        
    #To get hosts by name
    def get_hosts_by_name(self, from_mor):
        """
        Returns a dictionary of the existing ResourcePools. keys are their
        ManagedObjectReference objects and values their full path names.
        @from_mor: if given, retrieves the hosts contained within the specified 
            managed entity.
        """
        try:
            hosts_dic = self.server.get_hosts(from_mor)
        except:
            print "Get hosts error!"
            return None
        return hosts_dic
    
    def run_vm_by_name(self, name):
        """
        Run vm by name.
        """
        vm = self.server.get_vm_by_name(name, datacenter)
        status = vm.get_status()
        if status  == 'POWER_ON':
            pass
        else status == 'POWER_OFF':
            try:
                resault = vm.power_on()
            except:
                print "Run vm error!"
                pass
        
    def stop_vm_by_name(self, name):
        """
        Run vm by name.
        """
        vm = self.server.get_vm_by_name(name, datacenter)
        status = vm.get_status()
        if status  == 'POWER_OFF':
            pass
        else status == 'POWER_ON':
            try:
                resault = vm.power_off()
            except:
                print "Run vm error!"
                pass
    
    def get_vm_status_by_name(self, name):
        """
        Get vm status by nam
        """
        vm = self.server.get_vm_by_name(name, datacenter)
        status = vm.get_status()
        retrun status

    
        
