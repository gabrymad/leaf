from dataclasses import dataclass
import json
from logic.sensors import Endpoint, MoistureSensor


class Search:
    def __init__(self) -> None:
        self.current_query_text = ''

    def search(self, list_container:list[Endpoint], search_text:str):
        search_text = search_text.lstrip()
        search_text = search_text.rstrip()
        if search_text == self.current_query_text:
            return None
        self.current_query_text = search_text
        return list(filter(lambda x: search_text.lower() in x.name.lower(), list_container))

class Sort:
    def __init__(self) -> None:
        self.sorting_modes:list = [
            'Name',
            'Num sensors',
            'Mac address'
        ]
        self.current_sorting_mode = self.sorting_modes[0]
        self.sorting_modes.pop(0)
        self.current_is_reversed = False


    def sort(self, list_container:list[Endpoint], sorting_mode:str, is_reversed:bool):
        if sorting_mode == self.current_sorting_mode and is_reversed == self.current_is_reversed:
            return None
        if not sorting_mode == self.current_sorting_mode:
            self.sorting_modes.remove(sorting_mode)
            self.sorting_modes.append(self.current_sorting_mode)
        self.sorting_modes.sort()
        self.current_sorting_mode = sorting_mode
        self.current_is_reversed = is_reversed
        if sorting_mode == 'Name':
            return sorted(list_container,key=lambda x: x.name, reverse=is_reversed)
        if sorting_mode == 'Num sensors':
            return sorted(list_container,key=lambda x: x.get_num_sensors(), reverse=is_reversed)
        if sorting_mode == 'Mac address':
            return sorted(list_container,key=lambda x: x.mac_address, reverse=is_reversed)
            


def load_from_json():
    endpoints = []
    f = open('./web_page/data/endpoints.json')
    json_data = dict(json.load(f))
    #print(json_data)
    f.close()
    endpoint_dict_list = json_data['endpoints']
    for endpoint_dict in endpoint_dict_list:
        ep = Endpoint()
        ep.mac_address = endpoint_dict['mac_address']
        ep.set_name(endpoint_dict['name'])
        dict_sensor_list = endpoint_dict['sensor_list']
        for sensor_dict in dict_sensor_list:
            name = sensor_dict['name']
            if sensor_dict['class_instance'] == 'MoistureSensor':
                sensor = MoistureSensor(name)
            ep.add_sensor(sensor)
        ep.endpoint_status_code = endpoint_dict['endpoint_status_code']
        endpoints.append(ep)
    return endpoints