import plotly.graph_objects as go
import textwrap


def generate_visualizations(street_data_without, street_data_with, traffic_3, traffic, list_timeframe_in_seconds,
                            timeframe_from, timeframe_to, hideout, dict_names, title_size):
    """Generate visualizations comparing street data with and without deviations over a specified timeframe."""

    # Filter data to match selected timeframes
    df_without = street_data_without[street_data_without.columns.intersection(list_timeframe_in_seconds)].copy()
    df_with = street_data_with[street_data_with.columns.intersection(list_timeframe_in_seconds)].copy()

    # Compute mean for each street/vehicle
    df_without['mean'] = df_without.mean(axis=1)
    df_with['mean'] = df_with.mean(axis=1)

    # If specific streets or vehicles are selected, generate a figure for them
    if bool(dict_names):
        my_list = []  # *hideout.values()]
        for (key, value) in hideout.items():
            for v in value:
                my_list.append(v)
        fig = generate_figure(df_without, df_with, traffic_3, traffic, timeframe_from, timeframe_to, my_list, title_size)
        return fig
    else:
        # Otherwise, generate a figure for all streets/vehicles
        fig = generate_figure_all(df_without, df_with, traffic_3, traffic, timeframe_from, timeframe_to, title_size)
        return fig


def generate_figure_all(df_without, df_with, traffic_3, traffic, timeframe_from, timeframe_to, title_size):
    """Generate a histogram for all streets/vehicles comparing results with and without deviations."""

    # Create a figure with histograms comparing means
    figures = go.Figure()

    # Plot the data
    figures.add_trace(go.Histogram(x=df_without['mean'], name="Without deviations"))
    figures.add_trace(go.Histogram(x=df_with['mean'], name="With deviations"))

    # Create the plot title and adjust its formatting
    title = 'Frequency distribution of the results obtained by the vehicles in terms of ' + traffic_3 + ' for the time interval ' + timeframe_from + ' to ' + timeframe_to

    # Wrap the title text for better readability
    wrapped_title = '<br>'.join(textwrap.wrap(title, width=title_size))

    # Adjust title font size based on title size
    title_font_size = 16 if title_size != 30 else 12

    # Update the layout and title
    figures.update_layout(
        title_text=wrapped_title,
        xaxis_title_text=traffic,  # xaxis label
        yaxis_title_text='Number of vehicles',  # yaxis label
        bargap=0.2,  # gap between bars of adjacent location coordinates
        bargroupgap=0.1,  # gap between bars of the same location coordinates
        template = 'plotly_dark',
        font = dict(color='#deb522'),
        title={'y': 0.95, 'pad': {'b': 50}},
        title_font_size=title_font_size
    )
    return figures


def generate_figure(df_without, df_with, traffic_3, traffic, timeframe_from, timeframe_to, my_list, title_size):
    """Generate a histogram for selected streets/vehicles comparing results with and without deviations."""

    # Filter data based on the selected streets/vehicles
    df_without = df_without[df_without.index.isin(my_list)]
    df_with = df_with[df_with.index.isin(my_list)]

    figures = go.Figure()

    # Create a figure with histograms comparing means
    figures.add_trace(go.Histogram(x=df_without['mean'], name="Without deviations"))
    figures.add_trace(go.Histogram(x=df_with['mean'], name="With deviations"))

    title = 'Frequency distribution of the results obtained by the vehicles in terms of ' + traffic_3 + ' for the time interval ' + timeframe_from + ' to ' + timeframe_to

    # Wrap the title text for better readability
    wrapped_title = '<br>'.join(textwrap.wrap(title, width=title_size))

    # Adjust title font size based on title size
    title_font_size = 16 if title_size != 30 else 12

    # Update the layout and title
    figures.update_layout(
        title_text=wrapped_title,
        xaxis_title_text=traffic,  # xaxis label
        yaxis_title_text='Number of vehicles',  # yaxis label
        bargap=0.2,  # gap between bars of adjacent location coordinates
        bargroupgap=0.1,  # gap between bars of the same location coordinates
        template='plotly_dark',
        font=dict(color='#deb522'),
        title={'y': 0.95, 'pad': {'b': 50}},
        title_font_size=title_font_size
    )
    return figures
