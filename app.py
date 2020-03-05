import dash
import dash_core_components as dcc
import dash_html_components as html

from model import Sensor

sensor = Sensor()
data = list(sensor.get_data_by_time("2020-02-05"))
app = dash.Dash(__name__)

app.layout = html.Div(children=[
    html.H1(children='Sensor Monitor'),
    html.Div(id="output-clientside"),
    dcc.Graph(
        id='example-graph',
        figure={
            'data': [
                {
                    'type': 'scatter',
                    'x': data[0],
                    'y': data[1],
                    'mode':'line',
                    'name': 'Temperature'},
                {
                    'type': 'scatter',
                    'x': data[0],
                    'y': data[2],
                    'mode':'line',
                    'name': 'Humidity',
                    'yaxis':'y2'},
            ],
            'layout': {
                'width': '0.5',
                'height': '0.6',
                'title': 'Room Conditions Monitor',
                'xaxis': dict(title='DateTime'),
                'yaxis': dict(
                    title='Temperature/℃'),
                'yaxis2': dict(
                    title="Humidity/%",
                    overlaying='y',
                    side='right'
                )
            },
            # 'render_mode': 'webgl',
        }
    ),
])

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')
