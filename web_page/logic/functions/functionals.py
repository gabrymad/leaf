import json
from logic.sensors import Endpoint, MoistureSensor


def from_json():
    endpoints = []
    f = open('./web_page/data/endpoints.json')
    json_data = dict(json.load(f))
    print(json_data)
    f.close()
    endpoint_dict_list = json_data['endpoints']
    for endpoint_dict in endpoint_dict_list:
        ep = Endpoint()
        ep.mac_address = endpoint_dict['mac_address']
        ep.name = endpoint_dict['name']
        dict_sensor_list = endpoint_dict['sensor_list']
        for sensor_dict in dict_sensor_list:
            name = sensor_dict['name']
            if sensor_dict['class_instance'] == 'MoistureSensor':
                sensor = MoistureSensor(name)
            ep.add_sensor(sensor)
        ep.endpoint_status_code = endpoint_dict['endpoint_status_code']
        endpoints.append(ep)
    return endpoints