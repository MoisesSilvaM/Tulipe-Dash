from dash import Dash, html, dcc, Input, Output, State, callback, dash
import dash_bootstrap_components as dbc
import geojson
import dash_leaflet as dl
import re
from dash_extensions.javascript import arrow_function
from src.generate_visualizations_interval import generate_visualizations as generate_visualizations_byinterval
from src.generate_visualizations_streets import generate_visualizations as generate_visualizations_bystreets
from src.generate_visualizations_vehicles import generate_visualizations as generate_visualizations_byvehicles
from src.generate_visualizations_impacted import generate_visualizations as generate_visualizations_impacted
from src.const import *
import datetime
import os
import webbrowser
from threading import Timer
import optparse


# --- Initializing the app ---
dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc_css], title='TrafficTwin')
server = app.server


# --- Data loading functions ---

def convert_xml_to_csv(output_file_name, xmlfile):
    """Convert an XML file to CSV using SUMO tools."""
    if os.path.exists(xmlfile):
        os.system(
            f"python \"{os.path.join(os.environ['SUMO_HOME'], 'tools', 'xml', 'xml2csv.py')}\" {xmlfile} -o {output_file_name}")

def load_data(xmlfile, dataframe):
    """Convert XML to CSV and load data into a DataFrame."""
    file_name = 'edgedata.out.csv'
    convert_xml_to_csv(file_name, xmlfile)
    newdata = pd.read_csv(file_name, sep=";")
    frames = [dataframe, newdata]
    return pd.concat(frames)


def load_vehicles_data(xml_tripinfo_file):
    """Load vehicle data from an XML file and convert it to a CSV."""
    file_name = 'tripinfo.out.csv'
    convert_xml_to_csv(file_name, xml_tripinfo_file)
    return pd.read_csv(file_name, sep=";")


def sort_data(dataframe):
    """Sort the data by 'interval_begin' and 'edge_id'."""
    return dataframe.sort_values(by=['interval_begin', 'edge_id'], ignore_index=True)


# --- Input function ---
def read_inputs():
    """Read command-line inputs and load datasets for analysis."""
    parser = optparse.OptionParser()
    parser.add_option("--edgedata_without", action="append", dest="edgedata_without", default=[],
                      help="File without deviations", metavar="FILE_name_without")
    parser.add_option("--edgedata_with", action="append", dest="edgedata_with", default=[], help="File with deviations",
                      metavar="FILE_name_with")
    parser.add_option("--tripinfo_without", dest="tripinfo_without", help="Tripinfo file without deviations",
                      metavar="TRIPINFO_without")
    parser.add_option("--tripinfo_with", dest="tripinfo_with", help="Tripinfo file with deviations",
                      metavar="TRIPINFO_with")
    parser.add_option("--road_network_json", dest="road_network_json", help="TrafficTwin geojson", metavar="GeoJson")

    (options, args) = parser.parse_args()

    # Load data
    xml_edgedata_without = options.edgedata_without
    xml_edgedata_with = options.edgedata_with
    xml_tripinfo_without = options.tripinfo_without
    xml_tripinfo_with = options.tripinfo_with
    road_network_json_file = options.road_network_json

    dataframe_without = pd.DataFrame()
    dataframe_with = pd.DataFrame()

    # Load XML data into dataframes
    for xmldata_without in xml_edgedata_without:
        dataframe_without = load_data(xmldata_without, dataframe_without)
    dataframe_without = sort_data(dataframe_without)

    for xmldata_with in xml_edgedata_with:
        dataframe_with = load_data(xmldata_with, dataframe_with)
    dataframe_with = sort_data(dataframe_with)

    # Load vehicle data
    vehicle_data_without = load_vehicles_data(xml_tripinfo_without)
    vehicle_data_with = load_vehicles_data(xml_tripinfo_with)

    closed_roads = ["231483314", "832488061", "616545123", "150276002", "8384928", "606127853", "4730627", "4726710#0",
                    "627916937", "4726681#0"]  # This list has to come from the App (for now I left it like this)
    dict_names = {}

    return dataframe_without, dataframe_with, vehicle_data_without, vehicle_data_with, road_network_json_file, closed_roads, dict_names


# --- Defining global variables ---
dataframe_without, dataframe_with, vehicle_data_without, vehicle_data_with, road_network_json_file, closed_roads, dict_names = read_inputs()
url = 'https://tiles.stadiamaps.com/tiles/alidade_smooth_dark/{z}/{x}/{y}{r}.png'
attribution = '&copy; <a href="https://stadiamaps.com/">Stadia Maps</a> '

# --- Global time functions ---
def get_time_intervals_seconds():
    """Return unique time intervals from the data."""
    return dataframe_without['interval_id'].unique()


def get_time_intervals_string():
    """Convert time intervals from seconds to human-readable format."""
    intervals = get_time_intervals_seconds()
    return [
        f"{str(datetime.timedelta(seconds=int(re.split('_to_', interval)[0])))} to "
        f"{str(datetime.timedelta(seconds=int(re.split('_to_', interval)[1])))}"
        for interval in intervals]


def get_time_intervals_marks():
    """Return time interval marks for a slider input."""
    time_intervals_seconds = get_time_intervals_seconds()
    time_intervals_marks = [
        str(datetime.timedelta(seconds=int(re.split("_to_", elem)[0])))
        for elem in time_intervals_seconds
    ]
    last_interval_end = str(datetime.timedelta(seconds=int(re.split("_to_", time_intervals_seconds[-1])[1])))
    time_intervals_marks.append(last_interval_end)
    return time_intervals_marks


# --- Define global time variables ---
time_intervals_seconds = get_time_intervals_seconds()
time_intervals_string = get_time_intervals_string()
time_intervals_marks = get_time_intervals_marks()
len_time_intervals_string = len(time_intervals_string)


# --- Utility functions ---

def Color_scale():
    """Return a predefined color scale for the map plot."""
    return ["#0F9D58", "#fff757", "#fbbc09", "#E94335", "#822F2B"]


def read_geojson():
    """Read and return GeoJSON data from a file."""
    with open(road_network_json_file, encoding='utf-8') as f:
        return geojson.load(f)


def read_geojson_diff():
    """Read and return GeoJSON data from map_plot_diff file."""
    with open('map_plot_diff.geojson', encoding='utf-8') as f:
        return geojson.load(f)


def define_quantile(data_diff):
    """Return quantile intervals for the given data."""
    p1 = data_diff.quantile(q=0.25)
    p2 = data_diff.quantile(q=0.45)
    p3 = data_diff.quantile(q=0.65)
    p4 = data_diff.quantile(q=0.85)
    return [data_diff.min(), p1, p2, p3, p4, data_diff.max()]


def load_street_data(traffic):
    """Load and align street data for traffic without and with deviations."""
    df_without = detectors_out_to_table(dataframe_without, traffic).fillna(0)
    df_with = detectors_out_to_table(dataframe_with, traffic).fillna(0)
    return df_without.align(df_with, fill_value=0)


def open_browser():
    webbrowser.open_new("http://localhost:{}".format(8050))


# --- Time Interval functions ---

def get_from_time_intervals_string(time_intervals_seconds):
    """Extract the 'from' time from a list of time intervals."""
    interval_time = re.split(" to ", time_intervals_seconds[0])
    return interval_time[0]


def get_to_time_intervals_string(time_intervals_seconds):
    """Extract the 'to' time from a list of time intervals."""
    interval_time = re.split(" to ", time_intervals_seconds[-1])
    return interval_time[1]


def selected_timeframe_in_seconds(timeframe_split):
    """Convert a human-readable time split (hh:mm:ss) into total seconds.."""
    h1, m1, s1 = timeframe_split[0].split(':')
    starting = int(datetime.timedelta(hours=int(h1), minutes=int(m1), seconds=int(s1)).total_seconds())
    h2, m2, s2 = timeframe_split[2].split(':')
    end = int(datetime.timedelta(hours=int(h2), minutes=int(m2), seconds=int(s2)).total_seconds())
    return str(starting) + "_to_" + str(end)


# -- Generate options for the dropdown --
def generate_options_list():
    options_list = []
    if 'edge_traveltime' in dataframe_without.columns:
        options_list.append('Travel time (seconds)')
    if 'edge_density' in dataframe_without.columns:
        options_list.append('Density (vehicles/kilometres)')
    if 'edge_occupancy' in dataframe_without.columns:
        options_list.append('Occupancy (%)')
    if 'edge_timeLoss' in dataframe_without.columns:
        options_list.append('Time loss (seconds)')
    if 'edge_waitingTime' in dataframe_without.columns:
        options_list.append('Waiting time (seconds)')
    if 'edge_speed' in dataframe_without.columns:
        options_list.append('Speed (meters/seconds)')
    if 'edge_speedRelative' in dataframe_without.columns:
        options_list.append('Speed relative (average speed / speed limit)')
    if 'edge_sampledSeconds' in dataframe_without.columns:
        options_list.append('Sampled seconds (vehicles/seconds)')
    return options_list


dropdown_options = [{'label': title, 'value': title} for title in generate_options_list()]
dropdown_options_vehicles = [{'label': title, 'value': title} for title in
                             ['Duration (seconds)', 'Route length (meters)', 'Time loss (seconds)',
                              'Waiting time (seconds)']]
dropdown_options_timeframes = [{'label': title, 'value': title} for title in time_intervals_string]

offcanvas = html.Div([
    html.Div(id="filters",
             children=[html.H6("Filters")],
             style={'marginTop': '50px'},
             ),
    html.Div(id="street-ind",
             children="Street indicators",
             style={'marginTop': '15px'},
             ),
    dcc.Dropdown(
        id='traffic-dropdown',
        options=dropdown_options,
        value=generate_options_list()[0],
        placeholder='Select a traffic indicator...',
        searchable=True,
        style={'color': 'black'}
    ),
    html.Div(id="time-frames",
             children="Time frames",
             style={'marginTop': '25px'},
             ),
    html.Div([
        dcc.RangeSlider(min=0, max=len(time_intervals_marks) - 1, step=1, allowCross=False,
                        marks={(i): {'label': str(time_intervals_marks[i]),
                                     'style': {'transform': 'translateX(-20%) rotate(45deg)', "white-space": "nowrap",
                                               'margin-top': '10px', "fontSize": "14px", 'color': '#deb522'}} for i in
                               range(len(time_intervals_marks))},
                        value=[0, len(time_intervals_marks) - 1], id='my-range-slider'
                        ),
        html.Div(id='output-container-range-slider')
    ], className="dbc", style={'padding': '10px 20px 45px 0px'}
    ),
    html.Div(id='string_names',
             style={'marginTop': '15px'}),
    html.Div(id="select-street",
             children="Select the streets to analyze",
             style={'marginTop': '15px'},
             ),
    html.Div([
        dl.Map([
            dl.TileLayer(url=url, attribution=attribution),
            # From hosted asset (best performance).
            dl.GeoJSON(data=read_geojson(), id="geojson", hideout=dict(selected=[]), style=style_color,
                       hoverStyle=arrow_function(dict(weight=5, color='#00FFF7', dashArray='')),
                       onEachFeature=on_each_feature, )
        ], center=(50.82911264776447, 4.369035991425782), zoomControl=False, zoom=14,
            style={'height': '50vh', 'width': '100%'}),  # window height
    ], style={'border': '3px'}),
    dcc.Store(id='dict_names'),
], style={'backgroundColor': "black", 'color': '#deb522', 'width': '28%', "position": "fixed"}  # FIXING
)

app.layout = html.Div([
    dcc.Store(id='myDivInfo'),
    dcc.Store(id='titleSizeStore', data=None),
    dcc.Interval(id='interval-component', interval=500, n_intervals=0),
    dbc.Container([
        dbc.Row([
            dbc.Col(html.Div(id="Tulipe",
                             children=[html.H5("TrafficTwin")],
                             style={'marginTop': '5px', 'backgroundColor': "black", 'color': '#deb522', 'width': '28%',
                                    "position": "fixed"},  # style={'marginTop': '5px', 'color': '#deb522'},
                             ), width=5),
            dbc.Col(html.Div([' ']), width=5),  # Hasta aqui
            dbc.Col(html.Div([
                html.Div(["", dbc.Button("About us", outline=True, color="link", size="sm", className="me-1", id="open",
                                         n_clicks=0, style={'color': '#deb522'}),
                          "  ",
                          dbc.Button("Indicators", outline=True, color="link", size="sm", className="me-1",
                                     id="indicators_open", n_clicks=0, style={'color': '#deb522'})],
                         style={'text-align': 'right'}),
                dbc.Modal([
                    dbc.ModalHeader(dbc.ModalTitle("Machine Learning Group")),
                    dbc.ModalBody([modal_body]),
                ],
                    id="modal",
                    is_open=False,
                ),
                dbc.Modal([
                    dbc.ModalHeader(dbc.ModalTitle("Indicator description")),
                    dbc.ModalBody([traffic_body]),
                ],
                    id="indicators_modal",
                    is_open=False
                )]
            ), width=2)
        ]),
        dbc.Row([
            dbc.Col(offcanvas, width=5),
            dbc.Col(
                html.Div([
                    html.Div([
                        html.Div(id="summary",
                                 children=[html.H5("Summary")],
                                 style={'marginTop': '0px', 'color': '#deb522'},
                                 ),
                        html.Div(id="traffic_level",
                                 children=["Traffic level   : Medium traffic"],
                                 style={'marginTop': '5px', 'color': '#deb522'},
                                 ),
                        html.Div(id="time_intervals",
                                 children=["Time intervals: 12"],
                                 style={'marginTop': '5px', 'color': '#deb522'},
                                 ),
                        html.Div(id="street-deviations-results",
                                 children=["Map of Street Deviations:"],
                                 style={'marginTop': '5px', 'color': '#deb522'},
                                 ),
                        html.Div(
                            [
                                html.Div(id='description_map_plot'),
                                dcc.Store(id='map_view_state',
                                          data={'lat': 50.83401264776447, 'lng': 4.366035991425782, 'zoom': 15}),
                                dbc.Collapse(
                                    html.Div([
                                        dbc.Card(
                                            dbc.CardBody(
                                                html.Div([
                                                    # Aquí está el mapa
                                                    html.Div(id='map_plot'),
                                                ]),
                                                style={"padding": "0.1rem 0.1rem"}
                                            ),
                                            color='#deb522'
                                        ),
                                        html.Div(
                                            id="map_color_scale",
                                            style={"backgroundColor": "transparent", "padding": "10px"}
                                        )
                                    ]),
                                    id="collapse",
                                    is_open=True,
                                )
                            ]
                        ),
                        collapse_button,
                    ]),
                    html.Hr(
                        style={'borderWidth': "0.2vh", "width": "100%", "borderColor": "#deb522", "opacity": "unset"}),
                    html.Div(id="bystreets",
                             children=[html.H5("Results by streets")],
                             style={'marginTop': '5px', 'color': '#deb522'}
                             ),
                    dcc.Loading([html.Div(id='tabs-content')], type='default', color='#deb522'),
                    html.Br(),
                    html.Hr(
                        style={'borderWidth': "0.2vh", "width": "100%", "borderColor": "#deb522", "opacity": "unset"}),
                    html.Div(id="byvehicles",
                             children=[html.H5("Results by vehicles")],
                             style={'marginTop': '5px', 'color': '#deb522'}
                             ),
                    html.Div(id="vehicle-ind",
                             children="Vehicle indicators",
                             style={'marginTop': '15px', 'color': '#deb522'},
                             ),
                    dcc.Dropdown(
                        id='vehicle-dropdown',
                        options=dropdown_options_vehicles,
                        value='Duration (seconds)',
                        placeholder='Select a vehicular traffic indicator...',
                        searchable=True,
                        style={'color': 'black'}
                    ),
                    dcc.Loading([html.Div(id='tabs-content_vehicles')], type='default', color='#deb522'),
                ]), width=7)
        ])
    ], style={'backgroundColor': 'black', 'padding': '0px'})
], style={'backgroundColor': 'black', 'minHeight': '100vh'})


# --- Callback functions ---

# Clientside callback to get the window size
app.clientside_callback(
    """
    function(n_intervals, current_data) {
        var width = window.innerWidth;

        if (current_data && current_data.width === width) {
            return window.dash_clientside.no_update;
        }
        return {'width': width};
    }
    """,
    Output('myDivInfo', 'data'),
    Input('interval-component', 'n_intervals'),
    State('myDivInfo', 'data')  # Estado para obtener el tamaño de ventana actual almacenado
)


# Map update callback
@app.callback(
    [Output('description_map_plot', 'children'),
     Output('map_plot', 'children'), Output('map_color_scale', 'children')],
    [Input('traffic-dropdown', 'value'),
     Input('my-range-slider', 'value'),
     Input('map_view_state', 'data')]
)
def update_map_plot(traffic, timeframes, view_state):
    """Update the map plot based on selected traffic, timeframes, and view state."""
    list_timeframe_string = []
    list_timeframe_split = []
    list_timeframe_in_seconds = []
    if timeframes[0] != timeframes[1]:
        time_frames = list(range(timeframes[0], timeframes[1]))
    else:
        time_frames = list(range(0, len_time_intervals_string))

    [list_timeframe_string.append(time_intervals_string[i]) for i in time_frames]

    timeframe_from = get_from_time_intervals_string(list_timeframe_string)
    timeframe_to = get_to_time_intervals_string(list_timeframe_string)

    [list_timeframe_split.append(re.split(" ", list_timeframe_string[i])) for i in range(len(list_timeframe_string))]
    [list_timeframe_in_seconds.append(selected_timeframe_in_seconds(list_timeframe_split[i])) for i in
     range(len(list_timeframe_split))]

    traffic_indicator = "edge_" + get_traffic_name(traffic)

    data_diff, df_data = map_to_geojson(road_network_json_file, dataframe_without, dataframe_with,
                                        list_timeframe_in_seconds,
                                        traffic_indicator)
    colorscale = Color_scale()
    classes = define_quantile(data_diff)
    export_png(df_data, colorscale, classes, traffic_indicator)

    map_diff = dl.Map([
        dl.TileLayer(url=url, attribution=attribution),
        dl.GeoJSON(data=read_geojson_diff(), id="closed_roads_maps_with",
                   hideout=dict(colorscale=colorscale, classes=classes, colorProp=traffic_indicator, tname=traffic,
                                closed=closed_roads),
                   style=style_color_closed, zoomToBounds=True, onEachFeature=on_each_feature_closed)
    ], center=(50.82911264776447, 4.369035991425782), zoom=14, zoomControl=False, minZoom=14,
        style={'height': '56vh', 'width': '100%'}, id="map2")
    return (
        html.Div(
            [
                '- Showing the difference in terms of ' + traffic + ' for the time interval: ' + timeframe_from + ' to ' + timeframe_to],
            style={'color': '#deb522', 'text-indent': '1mm'}),
        html.Div([
            html.Div([map_diff], style={'backgroundColor': 'black', 'display': 'block', 'color': '#deb522'}),
        ]),
        html.Div(children=[
            html.Div('Color scale', style={'color': '#deb522'}),
            html.Div(children=[
                html.Div(f"{classes[i]:.2f} - {classes[i + 1]:.2f}",
                         style={"backgroundColor": colorscale[i], "height": "20px", "width": "200px",
                                "marginBottom": "5px",
                                "color": "black", "textAlign": "left"})
                for i in range(len(colorscale))
            ],
                style={"display": "flex", "flexDirection": "column", "alignItems": "left", "marginTop": "10px"}
            )
        ])
    )


# Collapse button callback
@app.callback(
    Output('collapse-button', 'children'),
    Input('collapse-button', 'n_clicks'))
def update_button(n_clicks):
    """Toggle button text based on the number of clicks."""
    return "Show map" if n_clicks % 2 else "Hide map"


# Modal toggle callback
@app.callback(Output("modal", "is_open"),
              [Input("open", "n_clicks")],
              [State("modal", "is_open")])
def toggle_modal(n1, is_open):
    """Toggle the visibility of the modal."""
    if n1:
        return not is_open
    return is_open


@app.callback(Output("indicators_modal", "is_open"),
              [Input("indicators_open", "n_clicks"),
               ],
              [State("indicators_modal", "is_open")])
def toggle_indicators_modal(n1, is_open):
    """Toggle the 'Indicators' modal."""
    if n1:
        return not is_open
    return is_open


@app.callback(
    Output("collapse", "is_open"),
    [Input("collapse-button", "n_clicks")],
    [State("collapse", "is_open")],
)
def toggle_collapse(n, is_open):
    """Toggle the collapse functionality for the closed streets section."""
    if n:
        return not is_open
    return is_open


# Font size update based on window width
@app.callback(
    Output('titleSizeStore', 'data'),
    Input('myDivInfo', 'data'),
    State('titleSizeStore', 'data')
)
def update_FontSize(myDivInfo, current_title_size):
    """Update the font size based on window width."""
    if myDivInfo is not None:
        window_width = myDivInfo['width']
        if window_width < 800:
            new_paragraph = 30
        elif window_width < 1000:
            new_paragraph = 40
        elif window_width < 1200:
            new_paragraph = 60
        elif window_width < 1400:
            new_paragraph = 70
        else:
            new_paragraph = 80

        if new_paragraph != current_title_size:
            return new_paragraph
    return dash.no_update


# Street selection callback
@app.callback(
    Output("geojson", "hideout"),
    Output('string_names', 'children'),
    Output('dict_names', 'data'),
    Input("geojson", "n_clicks"),
    State("geojson", "clickData"),
    State("geojson", "hideout"),
    prevent_initial_call=True)
def toggle_select(_, feature, hideout):
    """Handle street selection on the map."""
    selected = hideout["selected"]
    id = feature["properties"]["id"]
    name = feature["properties"]["name"]
    if id in selected:
        selected.remove(id)
        del dict_names[id]
    else:
        selected.append(id)
        dict_names[id] = name
    return hideout, html.Div(
        ['Selected street:'] + [html.Div(f"{value} (id:{key})") for (key, value) in dict_names.items()]), dict_names


# Traffic tab update callback
@app.callback(
    Output('tabs-content', 'children'),
    [Input('traffic-dropdown', 'value'),
     Input('my-range-slider', 'value'),
     Input("geojson", "hideout"),
     Input('titleSizeStore', 'data'),
     Input("geojson", "n_clicks")]
)
def update_tab(traffic, timeframes, hideout, title_size, string_names):
    """Update the content of the tabs based on selected traffic, time intervals, and selected streets."""
    list_timeframe_string = []
    list_timeframe_split = []
    list_timeframe_in_seconds = []
    if timeframes[0] != timeframes[1]:
        time_frames = list(range(timeframes[0], timeframes[1]))
    else:
        time_frames = list(range(0, len_time_intervals_string))
    [list_timeframe_string.append(time_intervals_string[i]) for i in time_frames]
    geo_data = read_geojson()
    street_data_without, street_data_with = load_street_data(get_traffic_name(traffic))
    traffic_name = get_traffic(traffic)
    traffic_lowercase = get_traffic_lowercase(traffic)
    timeframe_from = get_from_time_intervals_string(list_timeframe_string)
    timeframe_to = get_to_time_intervals_string(list_timeframe_string)

    [list_timeframe_split.append(re.split(" ", list_timeframe_string[i])) for i in range(len(list_timeframe_string))]
    [list_timeframe_in_seconds.append(selected_timeframe_in_seconds(list_timeframe_split[i])) for i in
     range(len(list_timeframe_split))]

    figure_bystreets = generate_visualizations_bystreets(street_data_without, street_data_with, traffic_name, traffic,
                                                         dict_names, list_timeframe_in_seconds, list_timeframe_string,
                                                         len_time_intervals_string, timeframe_from, timeframe_to,
                                                         title_size)
    figure_impacted = generate_visualizations_impacted(street_data_without, street_data_with, traffic_name,
                                                       traffic_lowercase, list_timeframe_in_seconds,
                                                       list_timeframe_string, len_time_intervals_string, geo_data,
                                                       hideout, dict_names, timeframe_from, timeframe_to, title_size)
    figure_byinterval = generate_visualizations_byinterval(street_data_without, street_data_with, traffic_name, traffic,
                                                           list_timeframe_in_seconds, timeframe_from, timeframe_to,
                                                           hideout, dict_names, title_size)
    street_condition = ""
    if bool(dict_names):
        impacted = "This figure shows the difference in " + traffic_lowercase + " of the selected streets, in two scenarios: with and without deviations."
        street = "The different lines correspond to the selected streets, and are identified with different colors."
    else:
        impacted = "This figure shows the 15 streets most impacted by the difference in " + traffic_lowercase + " in two scenarios: with and without deviations."
        street = "The lines correspond to the average of all the streets, and are identified with different colors."
    if len(dict_names) > 1:
        street_condition = " The legend on the right helps to identify which line belongs to which street and condition."
    return (
        html.Div([
            dcc.Graph(id='graph1', figure=figure_bystreets),
        ], style={'width': '100%', 'display': 'inline-block'}),
        html.Div(
            id="histogram_bystreet",
            children=[
                html.Div(
                    id="expl_bystreet_results",
                    children="This figure compares the " + traffic_name + " on streets over different time intervals. "
                                                                          "The horizontal axis represents the time intervals, while the vertical axis indicates the "
                             + traffic_lowercase + ". " + street + street_condition,
                ),
            ], style={'color': '#deb522'}),
        html.Br(),
        html.Hr(style={'borderWidth': "0.2vh", "width": "100%", "borderColor": "#deb522", "opacity": "unset"}),
        html.Div(id="byimpacted",
                 children=[html.H5("Results by impacted streets")],
                 style={'marginTop': '5px', 'color': '#deb522'}
                 ),
        html.Div([
            dcc.Graph(id='graph2', figure=figure_impacted, style={'height': '850px'}),
        ], style={'width': '100%', 'display': 'inline-block'}),
        html.Div(
            id="histogram5",
            children=[
                html.Div(
                    id="intro5_histogram",
                    children=impacted + "The horizontal axis shows the names of the affected streets, while the vertical "
                                        "axis shows the difference in " + traffic_lowercase + ". Higher bars indicate a larger difference. "
                                                                                              "Yellow labels above the bars indicate the exact time difference in hours:minutes format.",
                ),
            ], style={'color': '#deb522'}),
        html.Br(),
        html.Hr(style={'borderWidth': "0.2vh", "width": "100%", "borderColor": "#deb522", "opacity": "unset"}),
        html.Div(id="byinterval",
                 children=[html.H5("Results by time interval")],
                 style={'marginTop': '5px', 'color': '#deb522'}
                 ),
        html.Div([
            dcc.Graph(id='graph3', figure=figure_byinterval),
        ], style={'width': '100%', 'display': 'inline-block'}),
        html.Div(
            id="byinterval",
            children=[
                html.Div(
                    id="expl_byinterval_results",
                    children="The figure shows a comparison of the " + traffic_lowercase + " distribution in two scenarios: "
                                                                                           "with and without deviations in their route. The horizontal axis represents the " + traffic_lowercase +
                             " while the vertical axis shows the number of vehicles with those values. The blue bars correspond "
                             "to vehicles without deviations, and the red bars to vehicles with deviations.",
                ),
            ], style={'color': '#deb522'}),
    )


# Vehicle tab update callback
@app.callback(
    Output('tabs-content_vehicles', 'children'),
    [Input('vehicle-dropdown', 'value'),
     Input('titleSizeStore', 'data')]
)
def update_tab(vehicle, title_size):
    """Update the content of the vehicle tab based on selected vehicle indicator."""
    veh_traffic = get_veh_traffic(vehicle)
    veh_expl = get_veh_explanation(vehicle)
    figure_byvehicles = generate_visualizations_byvehicles(vehicle_data_without, vehicle_data_with,
                                                           get_vehicle_name(vehicle), veh_traffic, title_size)
    return (
        html.Div([
            dcc.Graph(id='graph4', figure=figure_byvehicles),
        ], style={'width': '100%', 'display': 'inline-block'}),
        html.Div(
            id="byvehicles",
            children=[
                html.Div(
                    id="intro4_histogram",
                    children="The figure shows a comparison of the distribution of the " + veh_expl + " in two scenarios: "
                                                                                                      "with and without deviations in their route. The horizontal axis represents the " + veh_traffic +
                             "while the vertical axis shows the number of vehicles with those values. The blue bars correspond "
                             "to vehicles without deviations, and the red bars to vehicles with deviations.",
                ),
            ], style={'color': '#deb522'})
    )


if __name__ == '__main__':
    Timer(1, open_browser).start()
    app.run_server(port=8050, host='127.0.0.1')
