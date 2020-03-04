import dash
import dash_core_components as dcc
import dash_html_components as html

app = dash.Dash()

app.layout = html.Div(children=[
    html.H1(children='你好，Dash'),

    html.Div(children='''
        Dash: Python网络应用框架'''),

    dcc.Graph(
        id='example-graph',
        figure={
            'data': [
                {'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': '北京'},
                {'x': [1, 2, 3], 'y': [2, 4, 5], 'type': 'bar', 'name': '天津'},
            ],
            'layout': {
                'title': 'Dash数据可视化'
            }
        }
    )
])

if __name__ == '__main__':
    app.run_server(debug=True,host='0.0.0.0')
