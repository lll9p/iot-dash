import dash
import dash_core_components as dcc
import dash_html_components as html

from model import Sensor

sensor = Sensor()
data = list(sensor.get_data_by_time("2020-02-23"))
app = dash.Dash()

app.layout = html.Div(children=[
    html.H1(children='传感器显示'),

    dcc.Graph(
        id='example-graph',
        figure={
            'data': [
                {'x': data[0],
                 'y': data[1],
                 'mode':'markers',
                 'name': '温度/℃'},
            ],
            'layout': {
                'title': '温度显示'
            }
        }
    ),
    dcc.Graph(
        id='example-graph2',
        figure={
            'data': [
                {'x': data[0],
                 'y': data[2],
                 'mode':'markers',
                 'name': '湿度/%'},
            ],
            'layout': {
                'title': '湿度显示'
            }
        }
    )
])

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')
