import datetime
from flask import Flask, Response, redirect, render_template, request
from logic.tools import load_from_json
import logic.tools as tools
import logic.models.sensor as se
from logic.models.basic import DataEntry
from logic.models.endpoint import Endpoint
from logic.models.cluster import EndpointCluster

app = Flask(__name__)
endpoints = EndpointCluster()
sorting_tool = tools.Sort()
searching_tool = tools.Search()

#
# HOMEPAGE VIEW
#
def _build_homepage():
    index_kwargs = {}
    eps = []
    end_list = searching_tool.search(endpoints.endpoint_list)
    searching_tool.set_search('')
    for endpoint in end_list:
        card_kwargs = {}
        sensors_prev_list = []
        endpoint.check_status()
        for sensor in endpoint.sensor_list:
            sensor_kwargs = {}
            sensor_kwargs['sensor_name'] = sensor.name+': '
            if sensor.binary_condition() == None:
                sensor_kwargs['text_color'] = 'no-data-text-theme'
            elif sensor.binary_condition() == True:
                sensor_kwargs['text_color'] = 'w3-text-yellow'
            else:
                sensor_kwargs['text_color'] = 'w3-text-green'
            sensor_kwargs['sensor_value'] = str(sensor.current_entry.value) + ' %' if not sensor.current_entry == None else 'None'
            sensors_prev_list.append(
                render_template(
                    '/homepage_previews/sensor_homepage_preview.html', 
                    **sensor_kwargs
                )
            )

        if endpoint.endpoint_status_code in [-1, None]:
            color="w3-badge w3-round-small no-data-theme"
        elif endpoint.endpoint_status_code == 0:
            color="w3-badge w3-round-small w3-green"
        elif endpoint.endpoint_status_code == 1:
            color="w3-badge w3-round-small warning-theme"
        else:
            color="w3-badge w3-round-small danger-theme"

        card_kwargs['endpoint_status_color'] = color
        card_kwargs['endpoint_page_path'] = endpoint.page_path()
        card_kwargs['sensor_card_list'] = sensors_prev_list
        card_kwargs['endpoint_name'] = endpoint.name
        card_kwargs['endpoint_addr'] = endpoint.mac_address
        eps.append(render_template(
            '/homepage_previews/endpoint_homepage_preview.html', 
            **card_kwargs)
        )  
    index_kwargs['endpoint_card_list'] = eps
    index_kwargs['options'] = sorting_tool.sorting_modes
    index_kwargs['current_select'] = sorting_tool.current_sorting_mode
    index_kwargs['check_box_value'] = sorting_tool.current_is_reversed
    return index_kwargs


# HOMEPAGE ROUTE
@app.route('/')
def home():
    index_kwargs = _build_homepage()
    return render_template(
        'index.html',
        **index_kwargs
    )

# HOMEPAGE OPERATIONS
@app.route('/search', methods=['POST'])
def search():
    text = request.form.get('search_text')
    
    searching_tool.set_search(text)
    return redirect('/')


@app.route('/sort', methods=['POST'])
def sort():
    method = request.form.get('sorting_method')
    is_reversed = 'is_reversed' in request.form
    print(method, is_reversed)
    print(sorting_tool.sorting_modes)
    output_list = sorting_tool.sort(endpoints.endpoint_list, method, is_reversed)
    if not output_list == None:
        endpoints.endpoint_list = output_list
    return redirect('/')


#
# ENDPOINT VIEW 
#
def _build_endpoint_page(endpoint_name:str):
    kwargs = {}
    endpoint = endpoints.get_endpoint_by_name(endpoint_name)
    if endpoint == None:
        return None
    endpoint.check_status()
    kwargs['endpoint_name'] = endpoint_name
    kwargs['endpoint_mac_address'] = endpoint.mac_address
    # last_update_text = '21/05/2023 23:21' 
    first_update_text = endpoint.get_first_update_as_str() if endpoint.first_update else 'No data'
    kwargs['endpoint_first_update'] = first_update_text
    last_update_text = endpoint.get_last_update_as_str() if endpoint.last_update else 'No data'
    kwargs['endpoint_last_update'] = last_update_text
    kwargs['num_sensors'] = ' '+ str(endpoint.get_num_sensors())
    #endpoint.update_timestamp()
    running_time_text = endpoint.get_running_time_as_str() if not endpoint.running_time == None else 'No data'
    kwargs['running_time'] = running_time_text

    if endpoint.endpoint_status_code in [-1, None]:
        color="no-data-theme"
        msg = 'No data'
    elif endpoint.endpoint_status_code == 0:
        color="w3-green"
        msg = 'Up and running'
    elif endpoint.endpoint_status_code == 1:
        color="warning-theme"
        msg = 'Probably disconnected'
    else:
        color="danger-theme w3-text-white"
        msg = 'Disconnected or damaged'

    kwargs['endpoint_status_color'] = color
    kwargs['endpoint_status_message'] = msg
    
    sensor_cards = []
    for sensor in endpoint.sensor_list:
        sensor_kwargs = {}
        sensor_type = sensor.class_instance
        sensor_name = sensor.name
        sensor_kwargs['endpoint_name'] = endpoint_name
        sensor_kwargs['sensor_type'] = sensor_type
        sensor_kwargs['sensor_name'] = sensor_name
        if sensor.class_instance == 'MoistureSensor':
            raw_value = str(sensor.current_entry.raw_value) if not sensor.current_entry == None else 'No data'
            percentage = str(sensor.current_entry.value) + ' %' if not sensor.current_entry == None else 'No data'
            sensor_kwargs['sensor_raw_value'] = raw_value 
            sensor_kwargs['sensor_value'] = percentage
            sensor_card = render_template('/sensor_cards/moisture_sensor_card.html', **sensor_kwargs)
        sensor_cards.append(sensor_card)
    kwargs['sensor_cards'] = sensor_cards
    return kwargs

# ENDPOINT ROUTE
@app.route('/endpoint/<endpoint_name>')
def endpoint_detail(endpoint_name:str):
    kwargs = _build_endpoint_page(endpoint_name)
    if kwargs == None:
        return redirect('/')
    return render_template('endpoint_detail.html', **kwargs)


#
# INSERT SENSOR VIEW
#
@app.route('/endpoint/<endpoint_name>/edit-sensor/<sensor_name>', methods=['GET', 'POST'])
def add_sensor(endpoint_name:str, sensor_name:str):
    kwargs = {}
    kwargs['input_endpoint_name'] = endpoint_name
    kwargs['endpoint_page_path'] = endpoints.get_endpoint_by_name(endpoint_name).page_path()
    return render_template('/update/update_sensor.html', **kwargs)


#
# INSERT ENDPOINT VIEW
#
@app.route('/endpoint/edit-endpoint/<endpoint_name>', methods=['GET', 'POST'])
@app.route('/edit-endpoint/<endpoint_name>', methods=['GET', 'POST'])
def add_endpoint(endpoint_name:str):
    return render_template('/update/update_endpoint.html')


#
# INSERT / DELETE
#
@app.route('/save-sensor', methods=['POST'])
def save_sensor():
    sensor_name = request.form.get('sensor-name-input')
    sensor_name = sensor_name.lstrip()
    sensor_name = sensor_name.rstrip()
    endpoint_name = request.form.get('endpoint-name-input')
    if len(endpoint_name) < 1:
        print(
            str(__name__).upper(),
            ': sensor [{name}] not valid, check length and whitespaces'.format(name=endpoint_name))
        return redirect('/')
    sensor = se.MoistureSensor(sensor_name)
    if endpoints.add_sensor_to_endpoint(endpoint_name, sensor):
        print(str(__name__).upper(),
            ': sensor [{name}] added correctly'.format(name=sensor_name))
        return redirect(endpoints.get_endpoint_by_name(endpoint_name).page_path())
    print(str(__name__).upper(),
            ': generic error')
    return redirect('/')

@app.route('/endpoint/<endpoint_name>/delete-sensor/<sensor_name>', methods=['GET', 'POST'])
def delete_sensor(endpoint_name:str, sensor_name:str):
    endpoints.delete_sensor_from_endpoint(endpoint_name, sensor_name)
    return redirect(endpoints.get_endpoint_by_name(endpoint_name).page_path())


@app.route('/save-endpoint', methods=['POST'])
def save_endpoint():
    endpoint_name = request.form.get('endpoint-name-input')
    endpoint_name = endpoint_name.lstrip()
    endpoint_name = endpoint_name.rstrip()
    a1 = request.form.get('endpoint-address-input1')
    a2 = request.form.get('endpoint-address-input2')
    a3 = request.form.get('endpoint-address-input3')
    a4 = request.form.get('endpoint-address-input4')
    a5 = request.form.get('endpoint-address-input5')
    a6 = request.form.get('endpoint-address-input6')
    endpoint_address = a1+':'+a2+':'+a3+':'+a4+':'+a5+':'+a6
    if len(endpoint_name) < 1:
        print(str(__name__).upper(),
            ': endpoint [{name}] not valid, check length and whitespaces'.format(name=endpoint_name))
        return redirect('/')
    if ' ' in endpoint_address or len(endpoint_address) < 17:
        print(str(__name__).upper(),
            ': endpoint [{name}] not valid, check length and whitespaces'.format(name=endpoint_address))
        return redirect('/')
    endpoint = Endpoint(endpoint_name, endpoint_address)
    if endpoints.add_endpoint(endpoint):
        print(str(__name__).upper(),
            ': endpoint [{name}] added correctly'.format(name=endpoint_name))
        return redirect(endpoint.page_path())
    print(str(__name__).upper(),
            ': generic error')
    return redirect('/')

@app.route('/endpoint/delete-endpoint/<endpoint_name>', methods=['GET', 'POST'])
@app.route('/delete-endpoint/<endpoint_name>', methods=['GET', 'POST'])
def delete_endpoint(endpoint_name:str):
    endpoints.delete_endpoint_by_name(endpoint_name)
    return redirect('/')


#
# DATA FROM ENDPOINTS
#
@app.route('/publish-data/<mac_address>', methods=['GET', 'POST'])
def get_data(mac_address:str):
    if mac_address in endpoints.mac_addresses():
        print(request.json)
        json_data = request.json
        sensor_id = json_data['sensor_id']
        raw_value = json_data['raw_value']
        entry = DataEntry()
        entry.date_time = datetime.datetime.now()
        entry.raw_value = raw_value
        if endpoints.update_endpoint_sensor(mac_address, sensor_id, entry):
            print(len(endpoints.get_endpoint_by_address(mac_address).sensor_list[sensor_id].sensor_reading_list))
            print(endpoints.get_endpoint_by_address(mac_address).sensor_list[sensor_id].entries())
            return Response(status=200)
    return Response(status=404)


if __name__ == '__main__':
    endpoint_list = load_from_json()
    endpoints.endpoint_list = endpoint_list
    endpoints.available_slots = 2
    app.run(debug=True)