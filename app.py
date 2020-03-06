import datetime

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as graph_objs
import plotly.subplots as subplots
from dash.dependencies import Input, Output

from config import debug
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
                        dcc.Interval(
                            id='interval-sensor',
                            interval=10 * 1000,
                            n_intervals=0
                        ),
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

                        ),
                        dcc.Graph(
                            id='sensor-graph',
                        ),
                    ]),
        ]),
    ])


sensor = Sensor()
# start_date = str(datetime.date.today() - datetime.timedelta(days=1))
# end_date = str(datetime.date.today())
# data = list(sensor.get_data_by_time(start_date, end_date))


@app.callback(Output(component_id='sensor-graph',
                     component_property='figure'),
              [Input(component_id='sensor-date-picker-range',
                     component_property='start_date'),
               Input(component_id='sensor-date-picker-range',
                     component_property='end_date'),
               Input(component_id='interval-sensor',
                     component_property='n_intervals')],
              )
def update_sensor_gragh(start_date, end_date, n_intervals):
    data = list(sensor.get_data_by_time(start_date, end_date))
    fig = subplots.make_subplots(rows=1, cols=1)
    trace_temperature = graph_objs.Scatter(
        x=data[0],
        y=data[1],
        mode='lines+markers',
        name='Temperature'
    )
    trace_humidity = graph_objs.Scatter(
        x=data[0],
        y=data[2],
        mode='lines+markers',
        name='Humidity'
    )
    fig.append_trace(trace_temperature, 1, 1)
    fig.append_trace(trace_humidity, 1, 1)
    with fig.batch_update():
        fig.data[1].update(yaxis='y2')
        fig.layout.update(
            # width=600, height=500,
            showlegend=True,
            legend=dict(x=0, y=1.2),
            xaxis=dict(
                title='Date',
                linecolor='black',
                mirror=True,
                # tickformat='%Y-%m-%d',
                tickmode='auto',
            ),
            yaxis1=dict(
                side='left',
                linecolor='black',
                title='Temperature(℃)'),
            yaxis2=dict(overlaying='y1',
                        side='right',
                        linecolor='black',
                        anchor='x1',
                        showgrid=True,
                        title='Humidity(%)'),
            hovermode='closest',
            annotations=[dict(
                x=data[0][-1],
                y=data[1][-1],
                text=f"{data[1][-1]:.1f}℃",
                showarrow=True,
                xref="x",
                yref="y"
            ),
                dict(
                x=data[0][-1],
                y=data[2][-1],
                text=f"{data[2][-1]:.1f}%",
                showarrow=True,
                xref="x",
                yref="y2"
            )
            ]

        )
    return fig


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
    app.run_server(debug=debug)
