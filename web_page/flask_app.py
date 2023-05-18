from flask import Flask, redirect, render_template, request
from logic.functions.functionals import from_json
from logic.sensors import Endpoint



app = Flask(__name__)
endpoint_list:list[Endpoint] = []
sort_options = ['Name', 'Last ping']
form_output= ['Sensor Number', True, '']
def _build_homepage(endpoint_list_temp):
    index_kwargs = {}
    eps = []
    for endpoint in endpoint_list_temp:
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
        else:
            color="w3-badge w3-round-medium w3-orange"

        card_kwargs['endpoint_status_color'] = color
        card_kwargs['sensor_card_list'] = sensors_prev_list
        card_kwargs['endpoint_name'] = endpoint.name
        card_kwargs['endpoint_addr'] = endpoint.mac_address
        eps.append(render_template('card.html', **card_kwargs))  
    index_kwargs['endpoint_card_list'] = eps
    index_kwargs['options'] = sort_options
    index_kwargs['current_select'] = form_output[0]
    index_kwargs['check_box_value'] = form_output[1]
    return index_kwargs


@app.route('/')
def home():
    list_temp = list(filter(lambda x: form_output[2].lower() in x.name.lower(), endpoint_list))
    index_kwargs = _build_homepage(list_temp)
    index_kwargs['input_text'] = form_output[2]
    return render_template(
        'index.html',
        **index_kwargs
    )


@app.route('/search', methods=['POST'])
def search():
    text = request.form.get('search_text')
    form_output[2] = text
    return redirect('/')

@app.route('/sort', methods=['POST'])
def select():
    sorting_method = request.form.get('sorting_method')
    check_box_value = 'is_reversed' in request.form

    current_select = form_output[0]
    if not sorting_method == current_select:
        sort_options.remove(sorting_method)
        sort_options.append(current_select)
        sort_options.sort()

    if sorting_method.lower() == 'name':
        endpoint_list.sort(key=lambda x:x.name, reverse=check_box_value)

    form_output[0] = sorting_method
    form_output[1] = check_box_value

    print(check_box_value)
    print(sorting_method)
    print(sort_options)

    return redirect('/')


if __name__ == '__main__':
    endpoint_list = from_json()
    app.run(debug=True)