from flask import Flask, render_template
from logic.functions.functionals import from_json
from logic.sensors import Endpoint



app = Flask(__name__)
endpoint_list:list[Endpoint] = []

@app.route('/')
def home():
    index_kwargs = {}
    eps = []
    for endpoint in endpoint_list:
        card_kwargs = {}
        sensors_prev_list = []
        for sensor in endpoint.sensor_list:
            sensor_kwargs = {}
            sensor_kwargs['sensor_name'] = sensor.name+': '
            if sensor.sensor_bool_flag == None:
                sensor_kwargs['text_color'] = 'w3-text-indigo'
            elif sensor.sensor_bool_flag == True:
                sensor_kwargs['text_color'] = 'w3-text-yellow'
            else:
                sensor_kwargs['text_color'] = 'w3-text-green'
            sensor_kwargs['sensor_value'] = sensor.current_entry.value if not sensor.current_entry == None else 'None'
            sensors_prev_list.append(render_template('sensor_preview.html', **sensor_kwargs))

        if endpoint.endpoint_status_code in [-1, None]:
            color="w3-badge w3-round-medium w3-indigo"
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
    return render_template(
        'index.html',
        **index_kwargs
    )

if __name__ == '__main__':
    endpoint_list = from_json()
    app.run(debug=True)