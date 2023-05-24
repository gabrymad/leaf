from __future__ import annotations
import datetime
from abc import ABC, abstractmethod



class DataEntry:
    def __init__(self) -> None:
        self.date_time:datetime.datetime = None
        self.raw_value:int = None
        self.value:float = None
    
    def __str__(self) -> str:
        return '(timestamp: '+self.date_time.strftime('%d/%m/%Y, %H:%M:%S')+' '+\
            'raw_value: '+str(self.raw_value)+' '+\
            'value: '+str(self.value)+')'


class Sensor(ABC):
    def __init__(
            self, 
            name:str,
            sensor_id:int,
            type:str=None) -> None:
        super().__init__()
        self.name:str = name
        self.id:int = sensor_id
        self.current_entry:DataEntry = None
        self.sensor_reading_list:list[DataEntry] = []
        self.sensor_bool_flag:bool = None
        self.class_instance:str = type

    @abstractmethod
    def update(self, new_entry:DataEntry):
        self.current_entry = new_entry
    
    @abstractmethod
    def update_entries_list(self):
        self.sensor_reading_list.append(self.current_entry)
        if len(self.sensor_reading_list) > 720:
            self.sensor_reading_list.pop(0)
    
    def get_datetime_as_string(self):
        return self.current_entry.date_time.strftime("%d/%m/%Y, %H:%M:%S") \
            if self.current_entry.date_time else None
    
    def entries(self):
        return [str(x) for x in self.sensor_reading_list]


class MoistureSensor(Sensor):
    def __init__(self, name: str, sensor_id:int) -> None:
        class_instance:str = str(type(self).__name__)
        super().__init__(name, sensor_id, class_instance)
        self.is_soil_dry:bool = None
        
    
    def update(self, new_entry: DataEntry):
        if not new_entry.raw_value == None:
            new_entry.raw_value = 1023 if new_entry.raw_value > 1023 else new_entry.raw_value
            new_entry.raw_value = 0 if new_entry.raw_value < 0 else new_entry.raw_value
        new_entry.value = round(((1023 - new_entry.raw_value) / 1023) * 100, 2)
        self.is_soil_dry = True if new_entry.value < 41.0 else False
        self.sensor_bool_flag = self.is_soil_dry
        super().update(new_entry)
    
    def update_entries_list(self):
        super().update_entries_list()


class Endpoint:
    def __init__(self, name:str=None, mac_address:str=None) -> None:
        name = name.lstrip()
        name = name.rstrip()
        self.mac_address:str = mac_address
        self.name:str = name
        self.sensor_list:list[Sensor] = []
        self.endpoint_status_code:int = None
        self.endpoint_page_path = 'endpoint/'+name.replace(' ', '%20')
        self.available_sensor_ids = [i for i in range(5)]
        
        self.first_update:datetime.datetime = None
        self.last_update:datetime.datetime = None
        self.running_time = None
    
    def update_timestamp(self):
        if self.first_update == None:
            self.first_update = datetime.datetime.now()
        self.last_update = datetime.datetime.now()
        if self.last_update and self.first_update:
            self.running_time = self.last_update - self.first_update
    
    def update(self, sensor_id:int, new_entry: DataEntry):
        for sensor in self.sensor_list:
            if sensor.id == sensor_id:
                sensor.update(new_entry)
                sensor.update_entries_list()
                print('sensor updated')
                return
    
    def set_name(self, name:str):
        self.name = name
        self.endpoint_page_path = 'endpoint/'+name

    def get_num_sensors(self):
        return len(self.sensor_list)
    
    def get_running_time_as_str(self):
        return str(self.running_time.days)+' days and '+str(datetime.timedelta(seconds=self.running_time.seconds))+' hours '
    
    def get_first_update_as_str(self):
        return self.first_update.strftime('%d/%m/%Y %H:%M')
    
    def get_last_update_as_str(self):
        return self.last_update.strftime('%d/%m/%Y %H:%M')
    
    def add_sensor(self, new_sensor:Sensor) -> None:
        if len(self.available_sensor_ids) < 1:
            print('no available ids')
            return
        for sensor in self.sensor_list:
            if sensor.name == new_sensor.name:
                print('Sensor name already exists')
                return
        sensor_id = self.available_sensor_ids.pop(0)
        new_sensor.id = sensor_id
        self.sensor_list.append(new_sensor)
    
    def delete_sensor_by_name(self, sensor_name:str):
        is_found = False
        for i in range(len(self.sensor_list)):
            sensor = self.sensor_list[i]
            if sensor.name == sensor_name:
                is_found = True
                break
        if is_found:
            sensor = self.sensor_list.pop(i)
            self.available_sensor_ids.append(sensor.id)
            self.available_sensor_ids.sort()
            print('sensor removed')
        else:
            print('sensor name not found')
                    
    
    def check_status(self):
        current_time = datetime.datetime.now()
        if not self.last_update == None:
            timedelta = abs((self.last_update - current_time).total_seconds())
            print(timedelta)
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

class EndpointList:
    def __init__(self) -> None:
        self.endpoint_list:list[Endpoint] = []
    
    def set_endpoint_list(self, endpoint_list:list[Endpoint]):
        self.endpoint_list = None
        self.endpoint_list = endpoint_list

    def add_endpoint(self, new_endpoint:Endpoint):
        for endpoint in self.endpoint_list:
            if endpoint.is_equals(new_endpoint):
                print('endpoint already present')
                return
        self.endpoint_list.append(new_endpoint)
    
    def add_sensor_to_endpoint(self, endpoint_name:str, sensor:Sensor):
        for endpoint in self.endpoint_list:
            if endpoint_name == endpoint.name:
                endpoint.add_sensor(sensor)
                
    def remove_endpoint(self, endpoint_name:str):
        is_found = False
        for i in range(len(self.endpoint_list)):
            e = self.endpoint_list[i]
            if e.name == endpoint_name:
                is_found = True
                break
        if is_found:
            self.endpoint_list.pop(i)
            print('endpoint removed')
            return
        print('endpoint not removed')
    
    def delete_sensor_from_endpoint(self, endpoint_name:str, sensor_name:str):
        for endpoint in self.endpoint_list:
            if endpoint_name == endpoint.name:
                endpoint.delete_sensor_by_name(sensor_name)
                break
    
    def update(self, mac_address:str, sensor_id:int, new_entry:DataEntry):
        for endpoint in self.endpoint_list:
            if endpoint.mac_address == mac_address:
                endpoint.update(sensor_id, new_entry)
                endpoint.update_timestamp()
                print('enpoint updated')
                return

    def get_endpoint_by_name(self, endpoint_name:str):
        for endpoint in self.endpoint_list:
            if endpoint_name == endpoint.name:
                return endpoint
        print('not endpoint found for:', endpoint_name)
    
    def is_endpoint_present(self, candidate:Endpoint):
        for endpoint in self.endpoint_list:
            if endpoint.name == candidate.name and endpoint.mac_address == candidate.mac_address:
                return True
        return False
    
    def get_endpoint_by_address(self, endpoint_addr:str):
        for endpoint in self.endpoint_list:
            if endpoint_addr == endpoint.mac_address:
                return endpoint
        print('not endpoint found for:', endpoint_addr)
    
    def mac_addresses(self):
        return [x.mac_address for x in self.endpoint_list]
    
    def names(self):
        return [x.name for x in self.endpoint_list]