import plotly.express as px
import datetime
import textwrap


def generate_visualizations(street_data_without, street_data_with, traffic_name, traffic_lowercase,
                            list_timeframe_in_seconds, list_timeframe_string, len_time_intervals_string, geo_data,
                            hideout, dict_names, timeframe_from, timeframe_to, title_size):
    """Generate visualizations based on the street data."""

    # If specific streets are selected in the hideout
    if bool(dict_names):
        my_list = []
        for (key, value) in hideout.items():
            for v in value:
                my_list.append(v)
        fig = generate_figure(street_data_without, street_data_with, traffic_name, traffic_lowercase,
                              list_timeframe_in_seconds, timeframe_from, timeframe_to, geo_data, my_list, title_size)
        return fig
    else:
        # Generate figure for the 15 most impacted streets
        fig = generate_figure_15_most_impacted(street_data_without, street_data_with, traffic_name, traffic_lowercase,
                                               list_timeframe_in_seconds, list_timeframe_string,
                                               len_time_intervals_string, geo_data, timeframe_from, timeframe_to,
                                               title_size)
        return fig


def generate_figure(street_data_without, street_data_with, traffic_name, traffic_lowercase, list_timeframe_in_seconds,
                    timeframe_from, timeframe_to, geojson, my_list, title_size):
    """Generate a bar plot for selected streets based on the difference between with and without deviations."""

    # Filter the data based on the selected streets
    df_without = street_data_without[street_data_without.columns.intersection(list_timeframe_in_seconds)].copy()
    df_with = street_data_with[street_data_with.columns.intersection(list_timeframe_in_seconds)].copy()
    df_without = df_without[df_without.index.isin(my_list)]
    df_with = df_with[df_with.index.isin(my_list)]

    # Calculate the mean for each street
    df_without['mean'] = df_without.mean(axis=1)
    df_with['mean'] = df_with.mean(axis=1)

    # Merge and calculate the difference
    df = df_without.merge(df_with, left_index=True, right_index=True, how="left")
    df['difference'] = df['mean_y'].sub(df['mean_x'], axis=0)

    # Apply appropriate transformation for time-based values
    if traffic_lowercase == 'time loss (seconds)' or traffic_lowercase == 'travel time (seconds)' or traffic_lowercase == 'waiting time (seconds)':
        df['diff_dates'] = df['difference'].apply(get_sec_to_date)
    else:
        df['diff_dates'] = df['difference'].apply(get_copy_sec)

    # Sort the selected streets
    df = df.sort_values(by=['diff_dates'], ascending=False)

    index_names = df.index.values.tolist()
    list_names = []

    title = 'Difference of the streets in terms of ' + traffic_name + ' for the time interval ' + timeframe_from + ' to ' + timeframe_to

    # Wrap the title text for better readability
    wrapped_title = '<br>'.join(textwrap.wrap(title, width=title_size))

    # Adjust title font size based on title size
    title_font_size, margin = adjust_title_formatting(title_size)

    # Map street names to the plot's x-axis
    for elem in index_names:
        for i in geojson['features']:
            if i["properties"].get("id") == elem:
                list_names.append(i["properties"].get("name") + ' (id:' + i["properties"].get("id") + ')')

    # generate bar plot
    fig = px.bar(df, y='diff_dates', x=df.index, orientation='v', text='diff_dates',
                 # color='diff_dates',
                 title=wrapped_title)
    if traffic_lowercase == 'time loss (seconds)' or traffic_lowercase == 'travel time (seconds)' or traffic_lowercase == 'waiting time (seconds)':
        fig.update_traces(texttemplate='%{text}', textposition='outside')
    else:
        fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')

    # Update the layout and title
    fig.update_layout(
        xaxis_title_text='Street',
        yaxis_title_text='Difference in ' + get_traffic_y_axis(traffic_name),
        template='plotly_dark',
        font=dict(color='#deb522'),
        xaxis=dict(tickmode='array',
                   tickvals=df.index,
                   ticktext=list_names),
        yaxis=dict(showticklabels=False),
        title={'y': 0.95, 'pad': {'b': 50}},
        title_font_size=title_font_size,
        autosize=True, margin=dict(t=margin))
    return fig


def generate_figure_15_most_impacted(street_data_without, street_data_with, traffic_name, traffic_lowercase,
                                     list_timeframe_in_seconds, list_timeframe_string, len_time_intervals_string,
                                     geo_data, timeframe_from, timeframe_to, title_size):
    """Generate a bar plot for the 15 most impacted streets based on the difference between with and without deviations."""
    df_without = street_data_without[street_data_without.columns.intersection(list_timeframe_in_seconds)].copy()
    df_with = street_data_with[street_data_with.columns.intersection(list_timeframe_in_seconds)].copy()

    # Calculate mean and difference
    df_without['mean'] = df_without.mean(axis=1)
    df_with['mean'] = df_with.mean(axis=1)
    df = df_without.merge(df_with, left_index=True, right_index=True, how="left")
    df['difference'] = df['mean_y'].sub(df['mean_x'], axis=0)

    # Sort and select top 15 impacted streets
    df = df.sort_values(by=['difference'], ascending=False).head(15)

    # Apply time transformation
    if traffic_lowercase == 'time loss (seconds)' or traffic_lowercase == 'travel time (seconds)' or traffic_lowercase == 'waiting time (seconds)':
        df['diff_dates'] = df['difference'].apply(get_sec_to_date)
    else:
        df['diff_dates'] = df['difference'].apply(get_copy_sec)
    index_names = df.index.values.tolist()
    list_names = []

    title = '15 most impacted streets in terms of ' + traffic_name + ' for the time interval ' + timeframe_from + ' to ' + timeframe_to

    # Wrap the title text for better readability
    wrapped_title = '<br>'.join(textwrap.wrap(title, width=title_size))

    # Adjust title font size and margin based on title size
    title_font_size, margin = adjust_title_formatting(title_size)

    # Map street names to the plot's x-axis
    for elem in index_names:
        for i in geo_data['features']:
            if i["properties"].get("id") == elem:
                list_names.append(i["properties"].get("name") + ' (id:' + i["properties"].get("id") + ')')

    # generate bar plot
    fig = px.bar(df, y='diff_dates', x=df.index, orientation='v', text='diff_dates',
                 # color='diff_dates',
                 title=wrapped_title
                 )
    if traffic_lowercase == 'time loss (seconds)' or traffic_lowercase == 'travel time (seconds)' or traffic_lowercase == 'waiting time (seconds)':
        fig.update_traces(texttemplate='%{text}', textposition='outside')
    else:
        fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')

    # Update the layout and title
    fig.update_layout(
        xaxis_title_text='Street',
        yaxis_title_text='Difference in ' + get_traffic_y_axis(traffic_name),
        template='plotly_dark',
        font=dict(color='#deb522'),
        xaxis=dict(tickmode='array',
                   tickvals=df.index,
                   ticktext=list_names,
                   tickangle=90),
        yaxis=dict(showticklabels=False),
        title={'y': 0.95, 'pad': {'b': 50}},
        title_font_size=title_font_size,
        autosize=True, margin=dict(t=margin))
    return fig


def get_sec_to_date(seconds):
    """Convert seconds to a time delta string (hh:mm:ss)."""
    sec = abs(seconds)
    return str(datetime.timedelta(seconds=int(sec)))


def get_copy_sec(seconds):
    """Return the seconds value as is for non-time-based metrics."""
    return abs(seconds)


def get_traffic_y_axis(traffic):
    """Return the label for the y-axis based on the traffic indicator."""
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
    """Determine if the traffic metric requires conversion to time format."""
    inf = False
    if traffic == 'time loss (seconds)':
        inf = True
    elif traffic == 'travel time (seconds)':
        inf = True
    return inf


def adjust_title_formatting(title_size):
    """Adjust the title font size and margin based on the provided title size."""
    title_font_size = 16
    margin = 100
    if title_size == 40:
        margin = 140
    elif title_size == 30:
        title_font_size = 12
        margin = 160
    return title_font_size, margin
