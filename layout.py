import datetime

import dash_core_components as dcc
import dash_html_components as html

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

layout = html.Div(
    children=[
        html.H1(children='Monitor'),
        dcc.Tabs(id='tabs', value='System State', persistence=True, children=[
            dcc.Tab(label='System State', value='tab-System',
                    style=tab_style,
                    selected_style=tab_selected_style,
                    children=[
                        html.H2(children='Machine Online'),
                        html.H2(children='NAS State'),
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
                            # min_date_allowed=datetime.date(2019, 5, 1),
                            initial_visible_month=datetime.date.today(),
                            end_date_placeholder_text='End date',
                            start_date_placeholder_text='Start date',
                            display_format='YYYY-MM-DD',
                            with_portal=True,
                            updatemode='bothdates',
                        ),
                        html.Button(
                            'Reflash graph.',
                            id='reflash-sensor-graph'),
                        dcc.Graph(
                            id='sensor-graph',
                        ),
                    ]),
        ]),
    ])
