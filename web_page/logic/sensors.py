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
            name:str) -> None:
        super().__init__()
        self.name:str = name
        self.current_entry:DataEntry = None
        self.sensor_reading_list:list[DataEntry] = []
        self.sensor_bool_flag:bool = None

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


class MoistureSensor(Sensor):
    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.is_soil_dry:bool = None
        self.class_instance:str = str(type(self).__name__)
    
    def update(self, new_entry: DataEntry):
        if not new_entry.raw_value == None:
            new_entry.raw_value = 1023 if new_entry.raw_value > 1023 else new_entry.raw_value
            new_entry.raw_value = 0 if new_entry.raw_value < 0 else new_entry.raw_value
        new_entry.value = (1023 - new_entry.raw_value) / 100
        self.is_soil_dry = True if new_entry.value < 41.0 else False
        self.sensor_bool_flag = self.is_soil_dry
        super().update(new_entry)
    
    def update_entries_list(self):
        super().update_entries_list()


class Endpoint:
    def __init__(self, name:str=None, mac_address:str=None) -> None:
        self.mac_address:str = mac_address
        self.name:str = name
        self.sensor_list:list[Sensor] = []
        self.endpoint_status_code:int = None
        self.endpoint_page_path = None
    

    def set_name(self, name:str):
        self.name = name
        self.endpoint_page_path = 'endpoint/'+name

    def get_num_sensors(self):
        return len(self.sensor_list)
    
    
    def add_sensor(self, new_sensor:Sensor) -> None:
        for sensor in self.sensor_list:
            if sensor.name == new_sensor.name:
                print('Sensor name already exists')
                return
        self.sensor_list.append(new_sensor)
        self.sensor_list.sort(key=lambda x: x.name, reverse=True)
    
    def delete_sensor_by_name(self, sensor_name:str):
        is_found = False
        for i in range(len(self.sensor_list)):
            sensor = self.sensor_list[i]
            if sensor.name == sensor_name:
                is_found = True
                break
        if is_found:
            self.sensor_list.pop(i)
            print('sensor removed')
        else:
            print('sensor name not found')
                    
    
    def check_status(self):
        self.endpoint_status_code = 0
    
    def is_equals(self, endpoint:Endpoint):
        return self.name == endpoint.name and self.mac_address == endpoint.mac_address

class EndpointList:
    def __init__(self) -> None:
        self.endpoint_list:list[Endpoint] = []
        self.search_query_endpoint_list:list[Endpoint] = None
    
    def set_endpoint_list(self, endpoint_list:list[Endpoint]):
        self.endpoint_list = None
        self.endpoint_list = endpoint_list

    def add_endpoint(self, new_endpoint:Endpoint):
        for endpoint in self.endpoint_list:
            if endpoint.is_equals(new_endpoint):
                print('endpoint already present')
                return
        self.endpoint_list.append(new_endpoint)

    def get_endpoint_by_name(self, endpoint_name:str):
        for endpoint in self.endpoint_list:
            if endpoint_name == endpoint.name:
                return endpoint
        print('not endpoint found for:', endpoint_name)
    
    def is_search_null(self):
        return self.search_query_endpoint_list == None
    