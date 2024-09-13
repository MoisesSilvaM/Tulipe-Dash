import plotly.graph_objects as go
import textwrap


def generate_visualizations(street_data_without, street_data_with, traffic_name, traffic, dict_names,
                            list_timeframe_in_seconds, list_timeframe_string, len_time_intervals_string, timeframe_from,
                            timeframe_to, title_size):
    if bool(dict_names):
        if len(dict_names) == 1:
            fig = generate_figure1(street_data_without, street_data_with, traffic_name, traffic, dict_names,
                                   list_timeframe_in_seconds, list_timeframe_string, len_time_intervals_string,
                                   timeframe_from, timeframe_to, title_size)
            return fig
        else:
            fig = generate_figure_some(street_data_without, street_data_with, traffic_name, traffic, dict_names,
                                       list_timeframe_in_seconds, list_timeframe_string, len_time_intervals_string,
                                       timeframe_from, timeframe_to, title_size)
            return fig
    else:
        mean_street_data_without = street_data_without.mean()
        mean_street_data_with = street_data_with.mean()
        fig = generate_figure_all(mean_street_data_without, mean_street_data_with, traffic_name, traffic,
                                  list_timeframe_in_seconds, list_timeframe_string, len_time_intervals_string,
                                  timeframe_from, timeframe_to, title_size)
        return fig


def generate_figure1(street_data_without, street_data_with, traffic_name, traffic, dict_names,
                     list_timeframe_in_seconds, list_timeframe_string, len_time_intervals_string, timeframe_from,
                     timeframe_to, title_size):
    name = ''
    fig1 = go.Figure()
    for (key, value) in dict_names.items():
        k = key
        name = value + ' (id:' + key + ')'
        street_data_without = street_data_without.loc[k]
        street_data_with = street_data_with.loc[k]
    if len(list_timeframe_in_seconds) != len_time_intervals_string:
        street_data_without = street_data_without.loc[street_data_without.index.isin(list_timeframe_in_seconds)]
        street_data_with = street_data_with.loc[street_data_with.index.isin(list_timeframe_in_seconds)]
        title = 'Comparing the ' + traffic_name + ' for the vehicles that originally passed through ' + name + ' for the time interval ' + timeframe_from + ' to ' + timeframe_to
    else:
        title = 'Comparing the ' + traffic_name + ' for the vehicles that originally passed through ' + name + ' for all the time intervals'
    wrapped_title = textwrap.wrap(title, width=title_size)
    wrapped_title_with_br = '<br>'.join(wrapped_title)
    title_font_size = 16
    margin = 100
    if title_size <= 40:
        title_font_size = 12
        margin = 160
    fig1.add_trace(go.Scatter(x=street_data_without.index, y=street_data_without.values,
                              mode='lines+markers',
                              name='without deviations'))
    fig1.add_trace(go.Scatter(x=street_data_with.index, y=street_data_with.values,
                              mode='lines+markers',
                              name='with deviations'))
    fig1.update_layout(yaxis_title=traffic)
    fig1.update_layout(
        title_text=wrapped_title_with_br,
        xaxis_title_text='Time interval',
    )
    fig1.update_layout(
        xaxis=dict(
            tickmode='array',
            tickvals=street_data_without.index,
            ticktext=list_timeframe_string)
    )
    fig1.update_layout(title={'y': 0.95, 'pad': {'b': 50}}, title_font_size=title_font_size)
    fig1.update_layout(autosize=True, margin=dict(t=margin))
    fig1.update_layout(template='plotly_dark', font=dict(color='#deb522'))
    return fig1


def generate_figure_some(street_data_without, street_data_with, traffic_name, traffic, dict_names,
                         list_timeframe_in_seconds, list_timeframe_string, len_time_intervals_string, timeframe_from,
                         timeframe_to, title_size):
    title = ''
    fig1 = go.Figure()
    for (key, value) in dict_names.items():
        k = key
        name = value + ' (id:' + key + ')'
        df_without = street_data_without.loc[k]
        df_with = street_data_with.loc[k]

        if len(list_timeframe_in_seconds) != len_time_intervals_string:
            df_without = df_without.loc[df_without.index.isin(list_timeframe_in_seconds)]
            df_with = df_with.loc[df_with.index.isin(list_timeframe_in_seconds)]
            title = ('Comparing the ' + traffic_name + (' for the vehicles that originally passed through some streets '
                                                        'for the time interval ') + timeframe_from + ' to ' +
                     timeframe_to)
        else:
            title = 'Comparing the ' + traffic_name + (' for the vehicles that originally passed through some ' +
                                                       'streets for all the time intervals')

        fig1.add_trace(go.Scatter(x=df_without.index, y=df_without.values,
                                  mode='lines+markers',
                                  name=name + '<br>without deviations'))
        fig1.add_trace(go.Scatter(x=df_with.index, y=df_with.values,
                                  mode='lines+markers',
                                  name=name + '<br>with deviations'))
        fig1.update_layout(yaxis_title=traffic)
    wrapped_title = textwrap.wrap(title, width=title_size)
    wrapped_title_with_br = '<br>'.join(wrapped_title)
    title_font_size = 16
    if title_size <= 40:
        title_font_size = 12
    fig1.update_layout(
        title_text=wrapped_title_with_br,
        xaxis_title_text='Time interval',
    )
    fig1.update_layout(
        xaxis=dict(
            tickmode='array',
            tickvals=df_without.index,
            ticktext=list_timeframe_string)
    )
    fig1.update_layout(title={'y': 0.95, 'pad': {'b': 50}}, title_font_size=title_font_size)
    fig1.update_layout(autosize=True, margin=dict(t=100))
    fig1.update_layout(template='plotly_dark', font=dict(color='#deb522'))
    return fig1


def generate_figure_all(mean_street_data_without, mean_street_data_with, traffic_name, traffic,
                        list_timeframe_in_seconds, list_timeframe_string, len_time_intervals_string, timeframe_from,
                        timeframe_to, title_size):
    if len(list_timeframe_in_seconds) != len_time_intervals_string:
        mean_street_data_without = mean_street_data_without.loc[
            mean_street_data_without.index.isin(list_timeframe_in_seconds)]
        mean_street_data_with = mean_street_data_with.loc[mean_street_data_with.index.isin(list_timeframe_in_seconds)]
        title = 'Comparing the average ' + traffic_name + ' on all the streets for the time interval ' + timeframe_from + ' to ' + timeframe_to
    #
    else:
        title = 'Comparing the average ' + traffic_name + ' on all the streets for all the time intervals'
    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(x=mean_street_data_without.index, y=mean_street_data_without.values,
                              mode='lines+markers',
                              name='without deviations'))
    fig1.add_trace(go.Scatter(x=mean_street_data_with.index, y=mean_street_data_with.values,
                              mode='lines+markers',
                              name='with deviations'))

    wrapped_title = textwrap.wrap(title, width=title_size)
    wrapped_title_with_br = '<br>'.join(wrapped_title)
    title_font_size = 16
    if title_size <= 40:
        title_font_size = 12
    fig1.update_layout(yaxis_title=traffic)
    fig1.update_layout(
        title_text=wrapped_title_with_br,
        xaxis_title_text='Time interval',
    )
    fig1.update_layout(
        xaxis=dict(
            tickmode='array',
            tickvals=mean_street_data_without.index,
            ticktext=list_timeframe_string
        )
    )
    fig1.update_layout(title={'y': 0.95, 'pad': {'b': 50}}, title_font_size=title_font_size)
    fig1.update_layout(template='plotly_dark', font=dict(color='#deb522'))
    return fig1
