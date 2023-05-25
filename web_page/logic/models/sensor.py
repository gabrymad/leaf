from .basic import Sensor, DataEntry

class MoistureSensor(Sensor):
    def __init__(self, name: str) -> None:
        class_instance:str = str(type(self).__name__)
        super().__init__(name, class_instance)
        self.is_soil_dry:bool = None
        
    
    def update(self, new_entry: DataEntry):
        if not new_entry.raw_value == None:
            new_entry.raw_value = 1023 if new_entry.raw_value > 1023 else new_entry.raw_value
            new_entry.raw_value = 0 if new_entry.raw_value < 0 else new_entry.raw_value
        new_entry.value = round(((1023 - new_entry.raw_value) / 1023) * 100, 2)
        self.is_soil_dry = True if new_entry.value < 41.0 else False
        super().update(new_entry)
    
    def update_entries_list(self):
        super().update_entries_list()
        
    def binary_condition(self):
        super().binary_condition()
        return self.is_soil_dry