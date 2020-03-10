import datetime

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as graph_objs
import plotly.subplots as subplots
from dash.dependencies import Input, Output
from callback import update_sensor_gragh,update_NAS_state_gragh
from layout import layout
from model import NASState, Sensor

sensor=Sensor()
class App(dash.Dash):
    def __init__(self):
        super().__init__(__name__)
        self.title = f"Monitor {datetime.date.today()}"
        self.css.config.serve_locally = True
        self.scripts.config.serve_locally = True
        self.layout = layout
        self.init_callbacks()
    def init_callbacks(self):
        @self.callback(Output('sensor-graph',
                 'figure'),
              [Input('sensor-date-picker-range',
                 'start_date'),
               Input('sensor-date-picker-range',
                 'end_date'),
               Input('reflash-sensor-graph',
                 'n_clicks'),
               # Input(component_id='interval-sensor',
               #       component_property='n_intervals')
               ],
              )
        def update_sensor_gragh_inner(start_date, end_date, n_clicks):
                return update_sensor_gragh(start_date, end_date, n_clicks,sensor)
        @self.callback(Output('NAS-state',
                     'children'),
                  [Input('show-NAS-state',
                     'n_clicks'),
                   Input('interval-NAS-state',
                     'n_intervals')],
                  )
        def update_NAS_state_gragh_inner(n_clicks, n_intervals):
                return update_NAS_state_gragh(n_clicks, n_intervals)


app = App()

server = app.server

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')
