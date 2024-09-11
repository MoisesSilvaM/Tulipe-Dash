import geopandas as gpd
import pandas as pd
import fiona  # don't remove please
import numpy as np
from dash_extensions.javascript import assign
from dash import html, dcc
import dash_bootstrap_components as dbc
import os

def detectors_out_to_table(sim_data_df, field_name):
    # parse all the intervals in the edgedata file
    traffic_indicator = "edge_" + field_name
    time_intervals = sim_data_df['interval_id'].unique()
    data_dict = {}
    for time_interval in time_intervals:
        # get the DF related to time_interval
        data_interval = sim_data_df.loc[sim_data_df['interval_id'] == time_interval]
        # get the IDs of the edges that has an edgedata output value in the current time interval
        list_edges = data_interval['edge_id'].unique()
        for edge_id in list_edges:
            # get the data for all the edges
            data = data_interval.loc[data_interval['edge_id'] == edge_id][traffic_indicator]
            if time_interval not in data_dict:
                data_dict[time_interval] = {}
            data_dict[time_interval][edge_id] = data.item()
    return pd.DataFrame.from_dict(data_dict)


def map_to_geojson(tulipe_geojson_file, edgedata_without, edgedata_with, interval, traffic_indicator):
    net_gdf = gpd.read_file(tulipe_geojson_file)
    net_gdf['index'] = net_gdf['id']
    net_gdf = net_gdf.set_index('index')

    street_data_without = edgedata_without.loc[edgedata_without['interval_id'].isin(interval)].copy()
    street_data_without = street_data_without.groupby('edge_id')[traffic_indicator].mean()

    street_data_with = edgedata_with.loc[edgedata_with['interval_id'].isin(interval)].copy()
    street_data_with = street_data_with.groupby('edge_id')[traffic_indicator].mean()

    diff = np.subtract(street_data_without, street_data_with)
    absolute_values = diff.abs()

    df_data = net_gdf.join(absolute_values).fillna(0)
    df_data.to_file('map_plot_diff.geojson')
    return absolute_values


tab_style = {
    'idle': {
        'borderRadius': '10px',
        'padding': '0px',
        'marginInline': '5px',
        'display': 'flex',
        'alignItems': 'center',
        'justifyContent': 'center',
        'fontWeight': 'bold',
        'backgroundColor': '#deb522',
        'border': 'none'
    },
    'active': {
        'borderRadius': '10px',
        'padding': '0px',
        'marginInline': '5px',
        'display': 'flex',
        'alignItems': 'center',
        'justifyContent': 'center',
        'fontWeight': 'bold',
        'border': 'none',
        'textDecoration': 'underline',
        'backgroundColor': '#deb522'
    }
}

style_color = assign("""function(feature, context){
    const {selected} = context.hideout;
    if(selected.includes(feature.properties.id)){   
        return {fillColor: '#b2b2b2', color: '#b2b2b2'} 
    }
    return {fillColor: '#1a73e8', color: '#1a73e8'}
}""")

style_color_closed = assign("""function(feature, context)
{
    const {colorscale, classes, colorProp, closed} = context.hideout;
    const value = feature.properties[colorProp];

    let fillColor;
    for (let i = 0; i < classes.length; ++i) {
        if (value > classes[i]) {
            fillColor = colorscale[i];  // set the fill color according to the class
        }
    }
    if(closed.includes(feature.properties.id)){   
        return {fillColor: '#a8a8a8', color: '#a8a8a8'} 
    }
    return {fillColor: fillColor, color: fillColor};
}
""")

on_each_feature = assign("""function(feature, layer, context){
    layer.bindTooltip(`${feature.properties.name} (id:${feature.properties.id})`)
}""")

on_each_feature_closed = assign("""function(feature, layer, context){
    const {colorProp, tname, closed} = context.hideout;
    if(closed.includes(feature.properties.id)){   
        layer.bindTooltip(`${feature.properties.name} (Closed street)`)
    }
    else{
        layer.bindTooltip(`${feature.properties.name} (${tname}: ${feature.properties[colorProp].toFixed()})`)
    }
}""")

modal_body = html.Div([
    html.Br(),
    html.B("Team: "), "Moisés Silva-Muñoz | Davide Andrea Guastella | Gianluca Bontempi",
    html.Br(), html.Br(),
    html.B("About: "),
    "The Machine Learning Group (MLG), founded in 2004 by G. Bontempi,  is a research unit of the Computer Science Department of the ULB (Université Libre de Bruxelles, Brussels, Belgium), Faculty of Sciences, currently co-headed by Prof. Gianluca Bontempi and Prof. Tom Lenaerts. MLG targets machine learning and behavioral intelligence research focusing on time series analysis, big data mining, causal inference, network inference, decision-making models and behavioral analysis with applications in data science, medicine, molecular biology, cybersecurity and social dynamics related to cooperation, emotions and others.",
    html.Br(), html.Br(),
    html.Div([
        html.A([html.Img(src=os.path.join("assets", "mlg.png"), height=50, className="rounded m-1")],
               href="https://mlg.ulb.ac.be/wordpress/", target="_blank"),
        html.A([html.Img(src=os.path.join("assets", "ulb.png"), height=50, className="rounded m-1")],
               href="https://www.ulb.be", target="_blank"),
    ])
])

traffic_body = html.Div([
    html.B("Traveltime: "), "Time in seconds needed to pass the street.",
    html.Br(),
    html.B("Density: "), "Vehicle density on the street (vehicles per km).",
    html.Br(),
    html.B("Occupancy: "),
    "Occupancy of the street in %. A value of 100 would indicate vehicles standing bumper to bumper on the whole street (minGap=0).",
    html.Br(),
    html.B("TimeLoss: "), "The average time lost due to driving slower than desired.",
    html.Br(),
    html.B("WaitingTime: "), "Sum of the time (in seconds) that vehicles are considered to be stopped.",
    html.Br(),
    html.B("Speed: "), "The mean speed (meters/seconds) on the street within the reported interval.",
    html.Br(),
    html.B("SpeedRelative: "), "Quotient of the average speed and the speed limit of the streets.",
    html.Br(),
    html.B("SampledSeconds: "), "Sum of vehicles on the street every second during the time interval.",
    html.Br(),
    html.B("Duration: "), "The average trip duration.",
    html.Br(),
    html.B("RouteLength: "), "The average route length.",
])

collapse_button = html.Div(
    [
        dbc.Button(
            "Closed streets", id="collapse-button", size="sm", className="mb-3", outline=True, color="warning",
            n_clicks=0, style={'marginTop': '1px'}),
    ]
)


def get_veh_traffic(traffic):
    value = ''
    if traffic == 'Duration (seconds)':
        value = 'duration of the trip (seconds) '
    if traffic == 'Route length (seconds)':
        value = 'length of the route (meters)'
    if traffic == 'Time loss (seconds)':
        value = 'time loss (seconds)'
    if traffic == 'Waiting time (seconds)':
        value = 'waiting time (seconds)'
    return value

def get_veh_explanation(traffic):
    value = ''
    if traffic == 'Duration (seconds)':
        value = 'duration of the trips of the vehicles (seconds) '
    if traffic == 'Route length (seconds)':
        value = 'length of the routes (meters)'
    if traffic == 'Time loss (seconds)':
        value = 'time loss by the vehicles (seconds)'
    if traffic == 'Waiting time (seconds)':
        value = 'waiting time of the vehicles (seconds)'
    return value

def get_vehicle_name(traffic):
    vehicle_df = ''
    if traffic == "Duration (seconds)":
        vehicle_df = "duration"
    elif traffic == "Route length (meters)":
        vehicle_df = "routeLength"
    elif traffic == "Time loss (seconds)":
        vehicle_df = "timeLoss"
    elif traffic == "Waiting time (seconds)":
        vehicle_df = "waitingTime"
    return vehicle_df


def get_traffic_lowercase(traffic):
    traffic_df = ''
    if traffic == "Density (vehicles/kilometres)":
        traffic_df = "density (vehicles/kilometres)"
    elif traffic == "Occupancy (%)":
        traffic_df = "occupancy (%)"
    elif traffic == "Time loss (seconds)":
        traffic_df = "time loss (seconds)"
    elif traffic == "Travel time (seconds)":
        traffic_df = "travel time (seconds)"
    elif traffic == "Waiting time (seconds)":
        traffic_df = "waiting time (seconds)"
    elif traffic == "Speed (meters/seconds)":
        traffic_df = "speed (meters/seconds)"
    elif traffic == "Speed relative (average speed / speed limit)":
        traffic_df = "speed relative (average speed/speed limit)"
    elif traffic == "Sampled seconds (vehicles/seconds)":
        traffic_df = "sampled seconds (vehicles/seconds)"
    return traffic_df


def get_traffic_name(traffic):
    traffic_df = ''
    if traffic == "Density (vehicles/kilometres)":
        traffic_df = "density"
    elif traffic == "Occupancy (%)":
        traffic_df = "occupancy"
    elif traffic == "Time loss (seconds)":
        traffic_df = "timeLoss"
    elif traffic == "Travel time (seconds)":
        traffic_df = "traveltime"
    elif traffic == "Waiting time (seconds)":
        traffic_df = "waitingTime"
    elif traffic == "Speed (meters/seconds)":
        traffic_df = "speed"
    elif traffic == "Speed relative (average speed / speed limit)":
        traffic_df = "speedRelative"
    elif traffic == "Sampled seconds (vehicles/seconds)":
        traffic_df = "sampledSeconds"
    return traffic_df


def get_traffic(traffic):
    inf = ''
    if traffic == "Density (vehicles/kilometres)":
        inf = "vehicle density (vehicles/kilometres)"
    elif traffic == "Occupancy (%)":
        inf = "vehicle occupancy (%)"
    elif traffic == "Time loss (seconds)":
        inf = "time lost by vehicles due to driving slower than the desired speed (seconds)"
    elif traffic == "Travel time (seconds)":
        inf = "travel time (seconds) of the vehicles"
    elif traffic == "Waiting time (seconds)":
        inf = "waiting time (seconds) of the vehicles"
    elif traffic == "Speed (meters/seconds)":
        inf = "average speed (meters/seconds) of the vehicles"
    elif traffic == "Speed relative (average speed / speed limit)":
        inf = "speed relative (average speed / speed limit) of the vehicles"
    elif traffic == "Sampled seconds (vehicles/seconds)":
        inf = "sampled seconds (vehicles/seconds) of the vehicles"
    return inf




