import datetime

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as graph_objs
import plotly.subplots as subplots
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate

from model import NASState, Sensor

sensor = Sensor()
start_date = str(datetime.date.today() - datetime.timedelta(days=1))
end_date = str(datetime.date.today())
data = list(sensor.get_data_by_time(start_date, end_date))
app = dash.Dash(__name__)

app.layout = html.Div(children=[
    html.H1(children='Monitor'),
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
    html.H2(children='NAS Monitor'),
    html.Button('Click here to view NAS state.', id='show-NAS-state'),
    html.Div(id='NAS-state'),
])


@app.callback(Output(component_id='sensor-graph',
                     component_property='figure'),
              [Input(component_id='sensor-date-picker-range',
                     component_property='start_date'),
               Input(component_id='sensor-date-picker-range',
                     component_property='end_date'),
               ]
              )
def update_sensor_gragh(start_date, end_date):
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
            hovermode='closest'

        )
    return fig


@app.callback(Output(component_id='NAS-state',
                     component_property='children'),
              [Input(component_id='show-NAS-state',
                     component_property='n_clicks')])
def update_NAS_state_gragh(n_clicks):
    # if n_clicks is None:
    #    raise PreventUpdate
    # else:
    NAS_state = NASState()
    return html.Pre(str(NAS_state))


if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')
