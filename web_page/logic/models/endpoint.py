from __future__ import annotations
import datetime
from .basic import Sensor, DataEntry



class Endpoint:
    def __init__(self, name:str=None, mac_address:str=None) -> None:
        name = name.lstrip()
        name = name.rstrip()
        self.mac_address:str = mac_address
        self.name:str = name
        self.sensor_list:list[Sensor] = []
        self.endpoint_status_code:int = None
        self.available_slots = 3
        
        self.first_update:datetime.datetime = None
        self.last_update:datetime.datetime = None
        self.running_time = None
    
    
    #
    # INSERT
    #
    def add_sensor(self, new_sensor:Sensor) -> bool:
        if self.available_slots < 1:
            print('no available slots')
            return False
        for sensor in self.sensor_list:
            if sensor.name == new_sensor.name:
                print('Sensor name already exists')
                return False
        self.sensor_list.append(new_sensor)
        self.available_slots -= 1
        return True
    
        
    #
    # UPDATE
    #
    def update_timestamp(self):
        if self.first_update == None:
            self.first_update = datetime.datetime.now()
        self.last_update = datetime.datetime.now()
        if self.last_update and self.first_update:
            self.running_time = self.last_update - self.first_update
    
    def update_sensor(self, sensor_name:str, new_entry: DataEntry):
        for sensor in self.sensor_list:
            if sensor.name == sensor_name:
                sensor.update(new_entry)
                sensor.update_entries_list()
                print('sensor updated')
                return

    
    #
    # DELETE
    #
    def delete_sensor_by_name(self, sensor_name:str):
        is_found = False
        for i in range(len(self.sensor_list)):
            sensor = self.sensor_list[i]
            if sensor.name == sensor_name:
                is_found = True
                break
        if is_found:
            sensor = self.sensor_list.pop(i)
            self.available_slots += 1
            print('sensor removed')
        else:
            print('sensor name not found')
    
    #
    # GETTERS
    #
    def get_num_sensors(self):
        return len(self.sensor_list)
    
    def get_running_time_as_str(self):
        return str(self.running_time.days)+' days and '+str(datetime.timedelta(seconds=self.running_time.seconds))+' hours '
    
    def get_first_update_as_str(self):
        return self.first_update.strftime('%d/%m/%Y %H:%M')
    
    def get_last_update_as_str(self):
        return self.last_update.strftime('%d/%m/%Y %H:%M')
    
    def page_path(self):
        return '/endpoint/'+self.name.replace(' ', '%20')
    
    def sensor_names(self):
        return [x.name for x in self.sensor_list]
    
    #
    # OTHER
    #
    def check_status(self):
        current_time = datetime.datetime.now()
        if not self.last_update == None:
            timedelta = (current_time - self.last_update).total_seconds()
            if timedelta < 0:
                print('wtf')
                return 
            if timedelta < 300:
                self.endpoint_status_code = 0
            elif timedelta >= 300 and timedelta < 600:
                self.endpoint_status_code = 1
            else:
                self.endpoint_status_code = 2
        else:
            self.endpoint_status_code = -1
    
    
    def is_equals(self, endpoint:Endpoint):
        return self.name == endpoint.name or self.mac_address == endpoint.mac_address

