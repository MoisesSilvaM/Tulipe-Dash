import plotly.express as px
import datetime


def generate_visualizations(street_data_without, street_data_with, traffic_name, traffic_lowercase,  list_timeframe_in_seconds, list_timeframe_string, len_time_intervals_string, geo_data, hideout, dict_names, timeframe_from, timeframe_to):
    if bool(dict_names):
        my_list = []
        for (key, value) in hideout.items():
            for v in value:
                my_list.append(v)
        fig = generate_figure(street_data_without, street_data_with, traffic_name, traffic_lowercase, list_timeframe_in_seconds, timeframe_from, timeframe_to, geo_data, my_list)
        return fig
    else:
        fig = generate_figure_15_most_impacted(street_data_without, street_data_with, traffic_name, traffic_lowercase,  list_timeframe_in_seconds, list_timeframe_string, len_time_intervals_string, geo_data, timeframe_from, timeframe_to)
        return fig


def generate_figure(street_data_without, street_data_with, traffic_name, traffic_lowercase, list_timeframe_in_seconds, timeframe_from, timeframe_to, geojson, my_list):
    df_without = street_data_without[street_data_without.columns.intersection(list_timeframe_in_seconds)].copy()
    df_with = street_data_with[street_data_with.columns.intersection(list_timeframe_in_seconds)].copy()
    df_without = df_without[df_without.index.isin(my_list)]
    df_with = df_with[df_with.index.isin(my_list)]

    df_without['mean'] = df_without.mean(axis=1)
    df_with['mean'] = df_with.mean(axis=1)

    df = df_without.merge(df_with, left_index=True, right_index=True, how="left")
    df['difference'] = df['mean_y'].sub(df['mean_x'], axis=0)

    if traffic_lowercase == 'time loss (seconds)' or traffic_lowercase == 'travel time (seconds)' or traffic_lowercase == 'waiting time (seconds)':
        df['diff_dates'] = df['difference'].apply(get_sec_to_date)
    else:
        df['diff_dates'] = df['difference'].apply(get_copy_sec)
    index_names = df.index.values.tolist()
    list_names = []
    for elem in index_names:
        for i in geojson['features']:
            if i["properties"].get("id") == elem:
                list_names.append(i["properties"].get("name") + ' (id:' + i["properties"].get("id") + ')')
    fig = px.bar(df, y='difference', x=df.index, orientation='v', text='diff_dates',
                 # color='diff_dates',
                 title='Difference of the streets in terms of ' + traffic_name + '<br>for the time interval ' +
                       timeframe_from + ' to ' + timeframe_to)
    if traffic_lowercase == 'time loss (seconds)' or traffic_lowercase == 'travel time (seconds)' or traffic_lowercase == 'waiting time (seconds)':
        fig.update_traces(texttemplate='%{text}', textposition='outside')
    else:
        fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
    fig.update_layout(xaxis_title_text='Street')
    fig.update_layout(yaxis_title_text='Difference in ' + get_traffic_y_axis(traffic_name))
    fig.update_layout(template='plotly_dark', font=dict(color='#deb522'))
    fig.update_layout(xaxis=dict(tickmode='array', tickvals=df.index, ticktext=list_names))
    fig.update_layout(yaxis=dict(showticklabels=False))
    return fig


def generate_figure_15_most_impacted(street_data_without, street_data_with, traffic_name, traffic_lowercase, list_timeframe_in_seconds, list_timeframe_string, len_time_intervals_string, geo_data, timeframe_from, timeframe_to):
    df_without = street_data_without[street_data_without.columns.intersection(list_timeframe_in_seconds)].copy()
    df_with = street_data_with[street_data_with.columns.intersection(list_timeframe_in_seconds)].copy()

    df_without['mean'] = df_without.mean(axis=1)
    df_with['mean'] = df_with.mean(axis=1)

    df = df_without.merge(df_with, left_index=True, right_index=True, how="left")
    df['difference'] = df['mean_y'].sub(df['mean_x'], axis=0)
    df = df.sort_values(by=['difference'], ascending=False).head(15)

    if traffic_lowercase == 'time loss (seconds)' or traffic_lowercase == 'travel time (seconds)' or traffic_lowercase == 'waiting time (seconds)':
        df['diff_dates'] = df['difference'].apply(get_sec_to_date)
    else:
        df['diff_dates'] = df['difference'].apply(get_copy_sec)
    index_names = df.index.values.tolist()
    list_names = []
    for elem in index_names:
        for i in geo_data['features']:
            if i["properties"].get("id") == elem:
                list_names.append(i["properties"].get("name") + ' (id:' + i["properties"].get("id") + ')')
    fig = px.bar(df, y='difference', x=df.index, orientation='v', text='diff_dates',
                 # color='diff_dates',
                 title='15 most impacted steets in terms of ' + traffic_name + '<br>for the time interval ' +
                       timeframe_from + ' to ' + timeframe_to,
                 )
    if traffic_lowercase == 'time loss (seconds)' or traffic_lowercase == 'travel time (seconds)' or traffic_lowercase == 'waiting time (seconds)':
        fig.update_traces(texttemplate='%{text}', textposition='outside')
    else:
        fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
    fig.update_layout(xaxis_title_text='Street')
    fig.update_layout(yaxis_title_text='Difference in ' + get_traffic_y_axis(traffic_name))
    fig.update_layout(template='plotly_dark', font=dict(color='#deb522'))
    fig.update_layout(xaxis=dict(tickmode='array', tickvals=df.index, ticktext=list_names, tickangle=90))
    fig.update_layout(yaxis=dict(showticklabels=False))
    return fig


def get_sec_to_date(seconds):
    if seconds < 0:
        sec = abs(seconds)
        dates = str(datetime.timedelta(seconds=int(sec)))
    else:
        dates = str(datetime.timedelta(seconds=int(seconds)))
    return dates


def get_copy_sec(seconds):
    return seconds


def get_traffic_y_axis(traffic):
    if traffic == "vehicle density (vehicles/kilometres)":
        inf = "density (vehicles/kilometres)"
    elif traffic == "vehicle occupancy (%)":
        inf = "occupancy (%)"
    elif traffic == "time lost by vehicles due to driving slower than the desired speed (seconds)":
        inf = "time loss (seconds)"
    elif traffic == "travel time (seconds) of the vehicles":
        inf = "travel time (hh:mm:ss)"
    elif traffic == "waiting time (seconds) of the vehicles":
        inf = "waiting time (seconds)"
    elif traffic == "average speed (meters/seconds) of the vehicles":
        inf = "speed (meters/seconds)"
    elif traffic == "speed relative (average speed / speed limit) of the vehicles":
        inf = "speed relative (average speed / speed limit)"
    elif traffic == "sampled seconds (vehicles/seconds) of the vehicles":
        inf = "sampled seconds (vehicles/seconds)"
    return inf


def get_response(traffic):
    inf = False
    if traffic == 'time loss (seconds)':
        inf = True
    elif traffic == 'travel time (seconds)':
        inf = True
    return inf
