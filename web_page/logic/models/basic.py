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
            type:str=None) -> None:
        super().__init__()
        self.name:str = name
        self.current_entry:DataEntry = None
        self.sensor_reading_list:list[DataEntry] = []
        self.class_instance:str = type
        self.id = None

    @abstractmethod
    def update(self, new_entry:DataEntry):
        self.current_entry = new_entry
    
    @abstractmethod
    def update_entries_list(self):
        self.sensor_reading_list.append(self.current_entry)
        if len(self.sensor_reading_list) > 720:
            self.sensor_reading_list.pop(0)
    
    @abstractmethod
    def binary_condition(self) -> bool:
        return None
    
    def get_datetime_as_string(self):
        return self.current_entry.date_time.strftime("%d/%m/%Y, %H:%M:%S") \
            if self.current_entry.date_time else None
    
    def entries(self):
        return [str(x) for x in self.sensor_reading_list]