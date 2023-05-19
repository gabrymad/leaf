from flask import Flask, redirect, render_template, request
from logic.functionals import load_from_json
from logic.sensors import Endpoint, EndpointList



app = Flask(__name__)
endpoints = EndpointList()
sort_options = ['Name', 'Last ping', 'Mac address']


def _build_homepage():
    index_kwargs = {}
    eps = []
    end_list = endpoints.endpoint_list if endpoints.search_query_endpoint_list==None else endpoints.search_query_endpoint_list
    for endpoint in end_list:
        card_kwargs = {}
        sensors_prev_list = []
        for sensor in endpoint.sensor_list:
            sensor_kwargs = {}
            sensor_kwargs['sensor_name'] = sensor.name+': '
            if sensor.sensor_bool_flag == None:
                sensor_kwargs['text_color'] = 'no-data-text-theme'
            elif sensor.sensor_bool_flag == True:
                sensor_kwargs['text_color'] = 'w3-text-yellow'
            else:
                sensor_kwargs['text_color'] = 'w3-text-green'
            sensor_kwargs['sensor_value'] = sensor.current_entry.value if not sensor.current_entry == None else 'None'
            sensors_prev_list.append(render_template('sensor_preview.html', **sensor_kwargs))

        if endpoint.endpoint_status_code in [-1, None]:
            color="w3-badge w3-round-medium no-data-theme"
        elif endpoint.endpoint_status_code == 0:
            color="w3-badge w3-round-medium w3-green"
        elif endpoint.endpoint_status_code == 1:
            color="w3-badge w3-round-medium warning-data-theme"
        else:
            color="w3-badge w3-round-medium danger-data-theme"

        card_kwargs['endpoint_status_color'] = color
        card_kwargs['sensor_card_list'] = sensors_prev_list
        card_kwargs['endpoint_name'] = endpoint.name
        card_kwargs['endpoint_addr'] = endpoint.mac_address
        eps.append(render_template('card.html', **card_kwargs))  
    index_kwargs['endpoint_card_list'] = eps
    index_kwargs['options'] = sort_options
    index_kwargs['current_select'] = endpoints.current_sort_method
    index_kwargs['check_box_value'] = endpoints.current_is_reversed
    return index_kwargs


@app.route('/')
def home():
    index_kwargs = _build_homepage()
    index_kwargs['input_text'] = endpoints.current_search_text
    return render_template(
        'index.html',
        **index_kwargs
    )


@app.route('/search', methods=['POST'])
def search():
    text = request.form.get('search_text')
    # form_output[2] = text
    endpoints.search(text)
    return redirect('/')


if __name__ == '__main__':
    endpoint_list = load_from_json()
    endpoints.set_endpoint_list(endpoint_list)
    
    app.run(debug=True)