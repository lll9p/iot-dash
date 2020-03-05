import datetime

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.tools as tools
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate

from model import NASState, Sensor

sensor = Sensor()
data = list(sensor.get_data_by_time("2020-02-05"))
app = dash.Dash(__name__)

app.layout = html.Div(children=[
    html.H1(children='Monitor'),
    html.H2(children='Sensor Monitor'),
    dcc.Input(id='date-input',
              type='Date',
              value=datetime.date.today()),
    dcc.Graph(
        id='sensor-graph',
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
    html.H2(children='NAS Monitor'),
    html.Button('Click here to view NAS state.', id='show-NAS-state'),
    html.Div(id='NAS-state'),
])


@app.callback(Output(component_id='NAS-state',
                     component_property='children'),
              [Input(component_id='show-NAS-state',
                     component_property='n_clicks')])
def update_NAS_state_gragh(n_clicks):
    if n_clicks is None:
        raise PreventUpdate
    else:
        NAS_state = NASState()
        return html.Pre(str(NAS_state))


if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')
