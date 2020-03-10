import plotly.graph_objs as graph_objs
from dash.dependencies import Input, Output

from model import NASState

def update_sensor_gragh(start_date, end_date, n_clicks,sensor):
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


def update_NAS_state_gragh(n_clicks, n_intervals):
    # if n_clicks is None:
    #    raise PreventUpdate
    # else:
    NAS_state = NASState()
    return str(NAS_state)
