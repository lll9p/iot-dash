import datetime

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as graph_objs
import plotly.subplots as subplots
from dash.dependencies import Input, Output

from model import NASState, Sensor

app = dash.Dash(__name__)

tabs_styles = {
    'height': '44px'
}
tab_style = {
    'borderBottom': '1px solid #d6d6d6',
    'padding': '6px',
    'fontWeight': 'bold'
}

tab_selected_style = {
    'borderTop': '1px solid #d6d6d6',
    'borderBottom': '1px solid #d6d6d6',
    'backgroundColor': '#119DFF',
    'color': 'white',
    'padding': '6px'
}

app.title = "Monitor"
app.css.config.serve_locally = True
app.scripts.config.serve_locally = True
app.layout = html.Div(
    children=[
        html.H1(children='Monitor'),
        dcc.Tabs(id='tabs', value='tab-NAS', children=[
            dcc.Tab(label='NAS State', value='tab-NAS',
                    style=tab_style,
                    selected_style=tab_selected_style,
                    children=[
                        html.H2(children='NAS Monitor'),
                        html.Button(
                            'Reflash NAS state.',
                            id='show-NAS-state'),

                        dcc.Interval(
                            id='interval-NAS-state',
                            interval=2 * 1000,
                            n_intervals=0
                        ),
                        dcc.Markdown(id='NAS-state'),
                    ]),
            dcc.Tab(label='Sensor Monitor', value='tab-Sensor',
                    style=tab_style,
                    selected_style=tab_selected_style,
                    children=[
                        html.H2(children='Sensor Monitor'),
                        dcc.DatePickerRange(
                            id='sensor-date-picker-range',
                            start_date=datetime.date.today(),
                            end_date=datetime.date.today(),
                            min_date_allowed=datetime.date(2019, 5, 1),
                            initial_visible_month=datetime.date.today(),
                            end_date_placeholder_text='End date',
                            start_date_placeholder_text='Start date',
                            display_format='YYYY-MM-DD',
                            with_portal=True,
                            updatemode='bothdates',
                        ),
                        # dcc.Interval(
                        #     id='interval-sensor',
                        #     interval=10 * 1000,
                        #     n_intervals=0
                        # ),

                        html.Button(
                            'Reflash graph.',
                            id='reflash-sensor-graph'),
                        dcc.Graph(
                            id='sensor-graph',
                        ),
                    ]),
        ]),
    ])


sensor = Sensor()
start_date = str(datetime.date.today() - datetime.timedelta(days=1))
end_date = str(datetime.date.today())


@app.callback(Output(component_id='sensor-graph',
                     component_property='figure'),
              [Input(component_id='sensor-date-picker-range',
                     component_property='start_date'),
               Input(component_id='sensor-date-picker-range',
                     component_property='end_date'),
               Input(component_id='reflash-sensor-graph',
                     component_property='n_clicks'),
               # Input(component_id='interval-sensor',
               #       component_property='n_intervals')
               ],
              )
def update_sensor_gragh(start_date, end_date, n_clicks):
    time, temperature, humidity = sensor.get_data_by_time(start_date, end_date)
    time = tuple(_.isoformat() for _ in time)
    trace_temperature = graph_objs.Scattergl(
        x=time,
        y=temperature,
        name='Temperature',
        mode='lines',
        yaxis='y1'
    )
    trace_humidity = graph_objs.Scattergl(
        x=time,
        y=humidity,
        name='Humidity',
        mode='lines',
        yaxis='y2'
    )
    traces = [trace_temperature, trace_humidity]
    return {
        'data': traces,
        'layout': dict(
            plot_bgcolor='#FFF',
            showlegend=True,
            legend=dict(x=0, y=1.2),
            xaxis=dict(
                title='Date',
                linecolor='black',
                mirror=True,
                # tickformat='%Y-%m-%d',
                tickmode='auto',
                type='date',
                ticks='inside',
            ),
            yaxis1=dict(
                side='left',
                linecolor='black',
                title='Temperature(℃)',
                ticks='inside',
            ),
            yaxis2=dict(overlaying='y1',
                        side='right',
                        linecolor='black',
                        anchor='x',
                        title='Humidity(%)',
                        ticks='inside',
                        ),
            hovermode='closest',
            annotations=[dict(
                x=time[-1],
                y=temperature[-1],
                text=f"{temperature[-1]:.1f}℃",
                showarrow=True,
                xref="x",
                yref="y1"
            ),
                dict(
                x=time[-1],
                y=humidity[-1],
                text=f"{humidity[-1]:.1f}%",
                showarrow=True,
                xref="x",
                yref="y2"
            )
            ]
        )
    }


@app.callback(Output(component_id='NAS-state',
                     component_property='children'),
              [Input(component_id='show-NAS-state',
                     component_property='n_clicks'),
               Input(component_id='interval-NAS-state',
                     component_property='n_intervals')],
              )
def update_NAS_state_gragh(n_clicks, n_intervals):
    # if n_clicks is None:
    #    raise PreventUpdate
    # else:
    NAS_state = NASState()
    return str(NAS_state)


server = app.server

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')
