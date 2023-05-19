from flask import Flask, redirect, render_template, request
from logic.tools import load_from_json
import logic.tools as tools
from logic.sensors import EndpointList



app = Flask(__name__)
endpoints = EndpointList()
sorting_tool = tools.Sort()
searching_tool = tools.Search()


def _build_homepage():
    index_kwargs = {}
    eps = []
    end_list = endpoints.endpoint_list if endpoints.is_search_null() else endpoints.search_query_endpoint_list
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
    index_kwargs['options'] = sorting_tool.sorting_modes
    index_kwargs['current_select'] = sorting_tool.current_sorting_mode
    index_kwargs['check_box_value'] = sorting_tool.current_is_reversed
    return index_kwargs


@app.route('/')
def home():
    index_kwargs = _build_homepage()
    index_kwargs['input_text'] = searching_tool.current_query_text
    return render_template(
        'index.html',
        **index_kwargs
    )


@app.route('/search', methods=['POST'])
def search():
    text = request.form.get('search_text')
    
    output_list = searching_tool.search(endpoints.endpoint_list, text)
    if not output_list == None:
        endpoints.search_query_endpoint_list = output_list
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


if __name__ == '__main__':
    endpoint_list = load_from_json()
    endpoints.set_endpoint_list(endpoint_list)
    
    app.run(debug=True)