import datetime
import plotly
import plotly.graph_objs as go
import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output
import random
import json
from carreralib import ControlUnit

class Driver(object):

    def __init__(self):
        self.laps = []
        self.bestlap = None
        self.lastlap = None
        self.inittime = None
        self.totaltime = None
        self.lapnumber = 0
        
    def new_lap(self, timer):
        if self.inittime is None:
            self.inittime = timer.timestamp
            self.totaltime = timer.timestamp
        else:
            laptime = timer.timestamp - self.totaltime
            self.lastlap = laptime
            if self.bestlap is None or laptime < self.bestlap:
                self.bestlap = laptime
            self.laps.append(laptime)
            self.lapnumber += 1
            self.totaltime = timer.timestamp

# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
external_stylesheets = [dbc.themes.BOOTSTRAP]


app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = dbc.Container([
        dbc.Row(
            html.Table([
                html.Tr([
                    html.Td(html.A('carreradash', href='https://github.com/erjosito/carreradash'), style={'width': '20%'}),
                    html.Td(html.H4('Race Management System'), style={'width': '60%'}),
                    html.Td(html.Img(src = 'https://upload.wikimedia.org/wikipedia/commons/thumb/6/60/Logo_Carrera.svg/2000px-Logo_Carrera.svg.png', width = 200), style={'width': '20%'})
                ])
            ], style={'width': '100%'})
        ),
        dbc.Row(
            [
                dbc.Col([
                    dbc.Row(html.H5("Car 1")),
                    dbc.Row(html.Div(id='car1'))
                ]),
                dbc.Col([
                    dbc.Row(html.H5("Car 2")),
                    dbc.Row(html.Div(id='car2'))
                ]),
            ]
        ),
        #dcc.Graph(id='cargraph',
        #         figure={
        #            'data': [{'x': [0], 'y': [0], 'type': 'line', 'name': 'Car 1'} ],
        #            'layout': go.Layout(title='Car 1 lap times', barmode='stack')
        #         }
        #),
        html.Div(id='cargraph'),
        html.Div(id='gapgraph'),
        html.Div(id='racedata', style={'display': 'none'}),
        html.Div([
            html.Button('Start', id='startbtn', n_clicks=0),
            html.Button('Reset', id='resetbtn', n_clicks=0),
            html.Div(id='btntimestamp', style={'display': 'none'})
        ]),
        dcc.Interval(
            id='interval-component',
            interval=1*1000, # in milliseconds
            n_intervals=0
        )
    ])

def msec2sec (msec):
    if msec == None:
        return 0
    else:
        return msec/1000

def update_data (race_data):
    data = cu.request()
    if isinstance(data, ControlUnit.Timer):
        print("Existing race data:", str(race_data))
        print("Calculating new values...")
        if data.address == 0 or data.address == 1:
            print("Updating timers for car 1")
            race_data[data.address].new_lap(data)
            print("Updated car", data.address, 'for lap', str(race_data[data.address].lapnumber))
        else:
            print("Timer received for unknown car {0}".format(str(data.address)))
    return race_data


@app.callback(Output('racedata', 'children'),
              Input('interval-component', 'n_intervals'))
def update_racedata(n):
    # Updata race data global variable so that other 
    global race_data
    race_data = update_data (race_data)

@app.callback(Output('car1', 'children'),
              Input('interval-component', 'n_intervals'))
def update_car1(n):
    position = None
    gap = 0
    if race_data[0].lapnumber > 0 and race_data[1].lapnumber > 0:
        common_laps = min(race_data[0].lapnumber, race_data[1].lapnumber)
        gap = sum(race_data[0].laps[:common_laps]) - sum(race_data[1].laps[:common_laps])
        if race_data[0].lapnumber > race_data[1].lapnumber:
            position = 1
        elif race_data[0].lapnumber < race_data[1].lapnumber:
            position = 2
        elif sum(race_data[0].laps[:common_laps]) < sum(race_data[1].laps[:common_laps]):
            position = 1
        else:
            position = 2
    style = {'padding': '5px', 'fontSize': '16px'}
    return [
        html.Ul([
            html.Li('Position: {0}'.format(position, style=style)),
            html.Li('Gap: {0:.3f}'.format(msec2sec(gap), style=style)),
            html.Li('Laps: {0}'.format(race_data[0].lapnumber, style=style)),
            html.Li('Last Lap: {0:.3f}'.format(msec2sec(race_data[0].lastlap), style=style)),
            html.Li('Best Lap: {0:.3f}'.format(msec2sec(race_data[0].bestlap), style=style)),
        ])
    ]


@app.callback(Output('car2', 'children'),
              Input('interval-component', 'n_intervals'))
def update_car2(n):
    position = None
    gap = None
    if race_data[0].lapnumber > 0 and race_data[1].lapnumber > 0:
        common_laps = min(race_data[0].lapnumber, race_data[1].lapnumber)
        gap = sum(race_data[1].laps[:common_laps]) - sum(race_data[0].laps[:common_laps])
        if race_data[0].lapnumber > race_data[1].lapnumber:
            position = 2
        elif race_data[0].lapnumber < race_data[1].lapnumber:
            position = 1
        elif sum(race_data[0].laps[:common_laps]) < sum(race_data[1].laps[:common_laps]):
            position = 2
        else:
            position = 1
    style = {'padding': '5px', 'fontSize': '16px'}
    return [
        html.Ul([
            html.Li('Position: {0}'.format(position, style=style)),
            html.Li('Gap: {0:.3f}'.format(msec2sec(gap), style=style)),
            html.Li('Laps: {0}'.format(race_data[1].lapnumber, style=style)),
            html.Li('Last Lap: {0:.3f}'.format(msec2sec(race_data[1].lastlap), style=style)),
            html.Li('Best Lap: {0:.3f}'.format(msec2sec(race_data[1].bestlap), style=style)),
        ])
    ]


#@app.callback(Output('cargraph', 'figure'),
#              Input('interval-component', 'n_intervals'))
#def update_cargraph(n):
@app.callback(Output(component_id='cargraph', component_property='children'),
              Input('interval-component', 'n_intervals'))
def render_graph(n):
    # Generate x,y axis for car 1
    if race_data[0].lapnumber > 0:
        x1_axis = list(range (1, race_data[0].lapnumber+1))
        y1_axis = race_data[0].laps
    else:
        x1_axis = [0]
        y1_axis = [0]
    # Generate x,y axis for car 2
    if race_data[1].lapnumber > 0:
        x2_axis = list(range (1, race_data[1].lapnumber+1))
        y2_axis = race_data[1].laps
    else:
        x2_axis = [0]
        y2_axis = [0]
    #if len(x_axis) == len(y_axis):
    #    print('Generating graph with', str(len(x_axis)), 'points. Variable types: x_axis is:', type(x_axis), 'and y_axis is', type(y_axis))
    #else:
    #    print('Error: x_axis has', str(len(x_axis)), 'points while y_axis has', str(len(y_axis)), 'points!')

    return [dcc.Graph(
        figure={
            'data': [
                {'x': x1_axis, 'y': y1_axis, 'type': 'line', 'name': 'Car 1'},
                {'x': x2_axis, 'y': y2_axis, 'type': 'line', 'name': 'Car 2'}
            ],
            'layout': go.Layout(title='Lap times')
         }               
        # Create the graph with subplots
        #fig = plotly.subplots.make_subplots(rows=1, cols=2, vertical_spacing=0.2, horizontal_spacing=0.2)
        #fig['layout']['margin'] = { 'l': 30, 'r': 10, 'b': 30, 't': 10 }
        #fig['layout']['legend'] = {'x': 0, 'y': 1, 'xanchor': 'left'}
        #fig.append_trace({
        #    'x': x_axis,
        #    'y': y_axis,
        #    'name': 'Lap times',
        #    'mode': 'lines+markers',
        #    'type': 'scatter'
        #}, 1, 1)
        #fig['layout']['legend'] = {'x': 0, 'y': 1, 'xanchor': 'left'}
        #fig.append_trace({
        #    'x': x_axis,
        #    'y': y_axis,
        #    'name': 'Lap times',
        #    'mode': 'lines+markers',
        #    'type': 'scatter'
        #}, 1, 2)
    )]

@app.callback(Output(component_id='gapgraph', component_property='children'),
              Input('interval-component', 'n_intervals'))
def render_gapgraph(n):
    # Generate x,y axis for gap (times of car1 - car2 at each lap)
    if race_data[0].lapnumber > 0 and race_data[1].lapnumber > 0:
        common_laps = min(race_data[0].lapnumber, race_data[1].lapnumber)
        gap = sum(race_data[0].laps[:common_laps]) - sum(race_data[1].laps[:common_laps])
        x1_axis = list(range (1, common_laps+1))
        y1_axis = [sum(race_data[0].laps[:i]) - sum(race_data[1].laps[:i]) for i in range (1, common_laps)]

    else:
        x1_axis = [0]
        y1_axis = [0]

    return [dcc.Graph(
        figure={
            'data': [
                {'x': x1_axis, 'y': y1_axis, 'type': 'bar', 'name': 'Car 1'}
            ],
            'layout': go.Layout(title='Gap times (negative values mean car 1 is winning)')
         }               
    )]


@app.callback(Output('btntimestamp', 'children'),
              Input('startbtn', 'n_clicks'))
def displayClick(startbtn):
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'startbtn' in changed_id:
        global race_data
        race_data = [Driver() for num in range(2)]
        print('Sending two consecutive start signals...')
        #sleep(1)
        cu.start()
        #sleep(1)
        cu.start()
        print ("Discarding existing timer data...")
        status = cu.request()
        while isinstance(status, ControlUnit.Timer):
            status = cu.request()
        msg = 'Sent Start signal to Control Unit'
    elif 'resetbtn' in changed_id:
        print('Resetting timers...')        
        cu.reset()
        msg = 'Sent Reset signal to Control Unit'
    else:
        msg = 'None of the buttons have been clicked yet'
    return html.Div(msg)


if __name__ == '__main__':
    # Initialize
    random.seed()
    print ("Initializing variables...")
    race_data = [Driver() for num in range(2)]
    print("Race data initialized to:", str(race_data))

    print ("Connecting to Carrera Control Unit...")
    cu = ControlUnit('EB:4F:00:8F:9E:AB')

    # Discard remaining timer messages
    print ("Discarding existing timer data...")
    status = cu.request()
    while not isinstance(status, ControlUnit.Status):
        status = cu.request()

    # Start web server
    print ("Starting web server...")
    app.run_server(use_reloader=False, debug=True, host="0.0.0.0")