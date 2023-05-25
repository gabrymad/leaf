from __future__ import annotations
import datetime
from .basic import Sensor, DataEntry
from .endpoint import Endpoint


class EndpointCluster:
    def __init__(self) -> None:
        self.endpoint_list:list[Endpoint] = []
        self.available_slots = 5
        
    #
    # INSERT
    #
    def add_endpoint(self, new_endpoint:Endpoint):
        if self.available_slots < 1:
            print('no available slots')
            return False
        for endpoint in self.endpoint_list:
            if endpoint.is_equals(new_endpoint):
                print('endpoint already present')
                return False
        self.endpoint_list.append(new_endpoint)
        self.available_slots -= 1
        return True
    
    def add_sensor_to_endpoint(self, endpoint_name:str, sensor:Sensor):
        for endpoint in self.endpoint_list:
            if endpoint_name == endpoint.name:
                return endpoint.add_sensor(sensor)
    
    
    #
    # UPDATE
    #
    def update_endpoint_sensor(self, mac_address:str, sensor_name:int, new_entry:DataEntry):
        for endpoint in self.endpoint_list:
            if endpoint.mac_address == mac_address:
                endpoint.update_sensor(sensor_name, new_entry)
                endpoint.update_timestamp()
                print('enpoint updated')
                return
    
    #
    # DELETE
    #
    def delete_endpoint_by_name(self, endpoint_name:str):
        is_found = False
        for i in range(len(self.endpoint_list)):
            e = self.endpoint_list[i]
            if e.name == endpoint_name:
                is_found = True
                break
        if is_found:
            self.endpoint_list.pop(i)
            self.available_slots += 1
            print('endpoint removed')
            return
        print('endpoint not removed')
    
    def delete_sensor_from_endpoint(self, endpoint_name:str, sensor_name:str):
        for endpoint in self.endpoint_list:
            if endpoint_name == endpoint.name:
                endpoint.delete_sensor_by_name(sensor_name)
                break
    
    
    #
    # GETTERS
    #
    def get_endpoint_by_name(self, endpoint_name:str):
        for endpoint in self.endpoint_list:
            if endpoint_name == endpoint.name:
                return endpoint
        print('not endpoint found for:', endpoint_name)
    
    def get_endpoint_by_address(self, endpoint_addr:str):
        for endpoint in self.endpoint_list:
            if endpoint_addr == endpoint.mac_address:
                return endpoint
        print('not endpoint found for:', endpoint_addr)
    
    def mac_addresses(self):
        return [x.mac_address for x in self.endpoint_list]
    
    def names(self):
        return [x.name for x in self.endpoint_list]
    
    
    #
    # OTHER
    #
    def is_endpoint_present(self, candidate:Endpoint):
        return candidate.name in self.names()