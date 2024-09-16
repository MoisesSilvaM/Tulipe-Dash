import plotly.graph_objects as go
import textwrap


def generate_visualizations(street_data_without, street_data_with, traffic_name, traffic, dict_names,
                            list_timeframe_in_seconds, list_timeframe_string, len_time_intervals_string, timeframe_from,
                            timeframe_to, title_size):
    """Generate visualizations comparing street data with and without deviations over a specified timeframe."""

    if bool(dict_names):  # Check if any specific streets are selected
        if len(dict_names) == 1:
            # If a single street is selected, generate a specific figure for it
            fig = generate_figure1(street_data_without, street_data_with, traffic_name, traffic, dict_names,
                                   list_timeframe_in_seconds, list_timeframe_string, len_time_intervals_string,
                                   timeframe_from, timeframe_to, title_size)
            return fig
        else:
            # If multiple streets are selected, generate a comparative figure for them
            fig = generate_figure_some(street_data_without, street_data_with, traffic_name, traffic, dict_names,
                                       list_timeframe_in_seconds, list_timeframe_string, len_time_intervals_string,
                                       timeframe_from, timeframe_to, title_size)
            return fig
    else:
        # If no specific streets are selected, generate a figure for all streets
        mean_street_data_without = street_data_without.mean()
        mean_street_data_with = street_data_with.mean()
        fig = generate_figure_all(mean_street_data_without, mean_street_data_with, traffic_name, traffic,
                                  list_timeframe_in_seconds, list_timeframe_string, len_time_intervals_string,
                                  timeframe_from, timeframe_to, title_size)
        return fig


def generate_figure1(street_data_without, street_data_with, traffic_name, traffic, dict_names,
                     list_timeframe_in_seconds, list_timeframe_string, len_time_intervals_string, timeframe_from,
                     timeframe_to, title_size):
    """Generate a figure comparing data for a single selected street over time."""

    name = ''
    fig1 = go.Figure()
    # Get the street data from the dictionary of selected streets
    for key, value in dict_names.items():
        street_data_without = street_data_without.loc[key]
        street_data_with = street_data_with.loc[key]
        name = f'{value} (id:{key})'

    # Filter data for selected timeframes
    if len(list_timeframe_in_seconds) != len_time_intervals_string:
        street_data_without = street_data_without.loc[street_data_without.index.isin(list_timeframe_in_seconds)]
        street_data_with = street_data_with.loc[street_data_with.index.isin(list_timeframe_in_seconds)]
        title = 'Comparing the ' + traffic_name + ' for the vehicles that originally passed through ' + name + ' for the time interval ' + timeframe_from + ' to ' + timeframe_to
    else:
        title = 'Comparing the ' + traffic_name + ' for the vehicles that originally passed through ' + name + ' for all the time intervals'

    # Wrap the title text for better readability
    wrapped_title = '<br>'.join(textwrap.wrap(title, width=title_size))

    # Adjust title font size and margin based on title size
    title_font_size = 12 if title_size <= 40 else 16
    margin = 160 if title_size <= 40 else 100

    # Plot the data
    fig1.add_trace(go.Scatter(x=street_data_without.index, y=street_data_without.values,
                              mode='lines+markers',
                              name='without deviations'))
    fig1.add_trace(go.Scatter(x=street_data_with.index, y=street_data_with.values,
                              mode='lines+markers',
                              name='with deviations'))

    # Update the layout and title
    fig1.update_layout(
        yaxis_title=traffic,
        title_text=wrapped_title,
        xaxis_title_text='Time interval',
        xaxis=dict(
            tickmode='array',
            tickvals=street_data_without.index,
            ticktext=list_timeframe_string),
        title={'y': 0.95, 'pad': {'b': 50}}, title_font_size=title_font_size,
        autosize=True, margin=dict(t=margin),
        template='plotly_dark',
        font=dict(color='#deb522'))
    return fig1


def generate_figure_some(street_data_without, street_data_with, traffic_name, traffic, dict_names,
                         list_timeframe_in_seconds, list_timeframe_string, len_time_intervals_string, timeframe_from,
                         timeframe_to, title_size):
    """Generate a figure comparing data for multiple selected streets over time."""

    title = ''
    fig1 = go.Figure()
    # Iterate through the selected streets
    for key, value in dict_names.items():
        df_without = street_data_without.loc[key]
        df_with = street_data_with.loc[key]
        name = f'{value} (id:{key})'

        # Filter data for selected timeframes
        if len(list_timeframe_in_seconds) != len_time_intervals_string:
            df_without = df_without.loc[df_without.index.isin(list_timeframe_in_seconds)]
            df_with = df_with.loc[df_with.index.isin(list_timeframe_in_seconds)]
            title = ('Comparing the ' + traffic_name + (' for the vehicles that originally passed through some streets '
                                                        'for the time interval ') + timeframe_from + ' to ' +
                     timeframe_to)
        else:
            title = 'Comparing the ' + traffic_name + (' for the vehicles that originally passed through some ' +
                                                       'streets for all the time intervals')

        # Plot the data for each street
        fig1.add_trace(go.Scatter(x=df_without.index, y=df_without.values,
                                  mode='lines+markers',
                                  name=name + '<br>without deviations'))
        fig1.add_trace(go.Scatter(x=df_with.index, y=df_with.values,
                                  mode='lines+markers',
                                  name=name + '<br>with deviations'))
        fig1.update_layout(yaxis_title=traffic)

    # Wrap the title text for better readability
    wrapped_title = '<br>'.join(textwrap.wrap(title, width=title_size))

    # Adjust title font size based on title size
    title_font_size = 16 if title_size <= 40 else 12

    # Update the layout and title
    fig1.update_layout(
        title_text=wrapped_title,
        xaxis_title_text='Time interval',
        xaxis=dict(
            tickmode='array',
            tickvals=df_without.index,
            ticktext=list_timeframe_string),
        title={'y': 0.95, 'pad': {'b': 50}},
        title_font_size=title_font_size,
        autosize=True,
        margin=dict(t=100),
        template='plotly_dark',
        font=dict(color='#deb522')
    )
    return fig1


def generate_figure_all(mean_street_data_without, mean_street_data_with, traffic_name, traffic,
                        list_timeframe_in_seconds, list_timeframe_string, len_time_intervals_string, timeframe_from,
                        timeframe_to, title_size):
    """Generate a figure comparing the average data of all streets over time."""

    # Filter data for selected timeframes
    if len(list_timeframe_in_seconds) != len_time_intervals_string:
        mean_street_data_without = mean_street_data_without.loc[
            mean_street_data_without.index.isin(list_timeframe_in_seconds)]
        mean_street_data_with = mean_street_data_with.loc[mean_street_data_with.index.isin(list_timeframe_in_seconds)]
        title = 'Comparing the average ' + traffic_name + ' on all the streets for the time interval ' + timeframe_from + ' to ' + timeframe_to
    #
    else:
        title = 'Comparing the average ' + traffic_name + ' on all the streets for all the time intervals'

    fig1 = go.Figure()
    # Plot the data for each street
    fig1.add_trace(go.Scatter(x=mean_street_data_without.index, y=mean_street_data_without.values,
                              mode='lines+markers',
                              name='without deviations'))
    fig1.add_trace(go.Scatter(x=mean_street_data_with.index, y=mean_street_data_with.values,
                              mode='lines+markers',
                              name='with deviations'))

    # Wrap the title text for better readability
    wrapped_title = '<br>'.join(textwrap.wrap(title, width=title_size))

    # Adjust title font size based on title size
    title_font_size = 16 if title_size <= 40 else 12

    # Update the layout and title
    fig1.update_layout(
        yaxis_title=traffic,
        title_text=wrapped_title,
        xaxis_title_text='Time interval',
        xaxis=dict(
            tickmode='array',
            tickvals=mean_street_data_without.index,
            ticktext=list_timeframe_string
        ),
        title={'y': 0.95, 'pad': {'b': 50}},
        title_font_size=title_font_size,
        template='plotly_dark',
        font=dict(color='#deb522')
    )
    return fig1
