import plotly.graph_objects as go
import textwrap


def generate_visualizations(street_data_without, street_data_with, traffic_3, traffic, list_timeframe_in_seconds,
                            timeframe_from, timeframe_to, hideout, dict_names):
    df_without = street_data_without[street_data_without.columns.intersection(list_timeframe_in_seconds)].copy()
    df_with = street_data_with[street_data_with.columns.intersection(list_timeframe_in_seconds)].copy()

    df_without['mean'] = df_without.mean(axis=1)
    df_with['mean'] = df_with.mean(axis=1)

    if bool(dict_names):
        my_list = []  # *hideout.values()]
        for (key, value) in hideout.items():
            for v in value:
                my_list.append(v)
        fig = generate_figure(df_without, df_with, traffic_3, traffic, timeframe_from, timeframe_to, my_list)
        return fig
    else:
        fig = generate_figure_all(df_without, df_with, traffic_3, traffic, timeframe_from, timeframe_to)
        return fig


def generate_figure_all(df_without, df_with, traffic_3, traffic, timeframe_from, timeframe_to):
    figures = go.Figure()
    figures.add_trace(go.Histogram(x=df_without['mean'], name="Without deviations"))
    figures.add_trace(go.Histogram(x=df_with['mean'], name="With deviations"))
    title = 'Frequency distribution of the results obtained by the vehicles in terms of ' + traffic_3 + ' for the time interval ' + timeframe_from + ' to ' + timeframe_to
    wrapped_title = textwrap.wrap(title, width=70)
    wrapped_title_with_br = '<br>'.join(wrapped_title)
    figures.update_layout(
        title_text=wrapped_title_with_br,
        xaxis_title_text=traffic,  # xaxis label
        yaxis_title_text='Number of vehicles',  # yaxis label
        bargap=0.2,  # gap between bars of adjacent location coordinates
        bargroupgap=0.1  # gap between bars of the same location coordinates
    )
    figures.update_layout(template='plotly_dark', font=dict(color='#deb522'))
    return figures


def generate_figure(df_without, df_with, traffic_3, traffic, timeframe_from, timeframe_to, my_list):
    df_without = df_without[df_without.index.isin(my_list)]
    df_with = df_with[df_with.index.isin(my_list)]
    figures = go.Figure()
    figures.add_trace(go.Histogram(x=df_without['mean'], name="Without deviations"))
    figures.add_trace(go.Histogram(x=df_with['mean'], name="With deviations"))
    title = 'Frequency distribution of the results obtained by the vehicles in terms of ' + traffic_3 + ' for the time interval ' + timeframe_from + ' to ' + timeframe_to
    wrapped_title = textwrap.wrap(title, width=70)
    wrapped_title_with_br = '<br>'.join(wrapped_title)
    figures.update_layout(
        title_text=wrapped_title_with_br,
        xaxis_title_text=traffic,  # xaxis label
        yaxis_title_text='Number of vehicles',  # yaxis label
        bargap=0.2,  # gap between bars of adjacent location coordinates
        bargroupgap=0.1  # gap between bars of the same location coordinates
    )
    figures.update_layout(template='plotly_dark', font=dict(color='#deb522'))
    return figures


def get_sec_to_date(seconds):
    min = seconds / 60
    return min
