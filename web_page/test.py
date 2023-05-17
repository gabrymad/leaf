from logic.sensors import DataEntry, MoistureSensor, Endpoint
import datetime
from getmac import get_mac_address as gma
from logic.functions.functionals import from_json


def test_data_class():
    value = DataEntry()
    value.date_time=datetime.datetime.now()
    value.value=None
    value.raw_value=255
    print(value)


def test_sensor():
    sensor = MoistureSensor('magic sensor')
    print(sensor.name)
    value = DataEntry()
    value.date_time=datetime.datetime.now()
    value.value=None
    value.raw_value=255
    sensor.update(value)
    sensor.update_entries_list()

    value = DataEntry()
    value.date_time=datetime.datetime.now()
    value.value=None
    value.raw_value=420
    sensor.update(value)
    sensor.update_entries_list()
    print(len(sensor.sensor_reading_list))


def test_endpoint():
    endpoint = Endpoint('endpoint_name', str(gma()))
    print(endpoint.name, endpoint.mac_address)

def test_load():
    eps = from_json()
    print(len(eps))
    print(eps[0].name)

if __name__=='__main__':
    print('test_data_class()')
    test_data_class()
    print('test_sensor()')
    test_sensor()
    print('test_endpoint()')
    test_endpoint()

    test_load()