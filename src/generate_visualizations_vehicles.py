import plotly.express as px
import plotly.graph_objects as go
import textwrap


def generate_visualizations(vehicle_data_without, vehicle_data_with, vehicle, veh_traffic, title_size):
    traffic_indicator = "tripinfo_" + vehicle
    vehicle_data_without = vehicle_data_without.loc[:,
                           ['tripinfo_id',
                            traffic_indicator]]
    vehicle_data_with = vehicle_data_with.loc[:,
                        ['tripinfo_id',
                         traffic_indicator]]

    # Generate the histogram figure comparing both datasets
    fig1 = generate_figure1(vehicle_data_without, vehicle_data_with, veh_traffic, traffic_indicator, title_size)
    return fig1


def generate_figure1(vehicle_data_without, vehicle_data_with, veh_traffic, traffic_indicator, title_size):
    """Generate a histogram comparing vehicle data for selected traffic indicators."""
    fig1 = go.Figure()

    # Add histogram traces for both datasets
    fig1.add_trace(go.Histogram(x=vehicle_data_without[traffic_indicator], name="Without deviations"))
    fig1.add_trace(go.Histogram(x=vehicle_data_with[traffic_indicator], name="With deviations"))

    # Wrap the title text for better readability
    title = 'Frequency distribution of the results obtained by the vehicles in terms of ' + veh_traffic + ' for the whole simulation'
    wrapped_title = '<br>'.join(textwrap.wrap(title, width=title_size))

    # Adjust title font size based on title size
    title_font_size = 16 if title_size != 30 else 12

    # Update figure layout
    fig1.update_layout(
        title_text=wrapped_title,
        # title of plot
        xaxis_title_text=veh_traffic,  # xaxis label
        yaxis_title_text='Number of vehicles',  # yaxis label
        bargap=0.2,  # gap between bars of adjacent location coordinates
        bargroupgap=0.1,  # gap between bars of the same location coordinates
        title={'y': 0.95, 'pad': {'b': 50}},
        title_font_size=title_font_size,
        template='plotly_dark',
        font=dict(color='#deb522')
    )
    return fig1


def generate_figure2(vehicle_data_without, vehicle_data_with, traffic, traffic_indicator, title_size):
    """Generate a bar chart comparing the top 15 most impacted vehicles in terms of traffic metrics."""

    # Set up vehicle IDs as string index
    vehicle_data_without['id'] = vehicle_data_without['tripinfo_id'].astype(str)
    vehicle_data_without = vehicle_data_without.set_index('tripinfo_id')
    vehicle_data_with = vehicle_data_with.set_index('tripinfo_id')

    # Merge data and calculate differences
    df = vehicle_data_without.merge(vehicle_data_with, left_index=True, right_index=True, how="left")
    value_x = traffic_indicator + '_x'
    value_y = traffic_indicator + '_y'

    # Compute the difference and fill NaN values
    df['diff'] = df[value_y].sub(df[value_x], axis=0).fillna(0)
    df[value_x] = df[value_x].fillna(0)
    df[value_y] = df[value_y].fillna(0)

    # Sort by the difference and select the top 15 impacted vehicles
    df = df.sort_values(by=['diff'], ascending=False).head(15)

    # Define the y-axis label based on traffic type
    value = ''
    if traffic == 'duration':
        value = 'duration (s)'
    if traffic == 'timeLoss':
        value = 'time loss (s)'
    if traffic == 'waitingTime':
        value = 'waiting time (s)'

    # Title for the chart
    title = '15 most impacted vehicles in terms of ' + value + ' comparing with and without deviations'
    wrapped_title = '<br>'.join(textwrap.wrap(title, width=title_size))

    # Adjust title font size
    title_font_size = 16 if title_size != 30 else 12

    # Generate the bar chart
    fig2 = px.bar(df, y='diff', x='id', orientation='v',
                  color='diff', text='diff',
                  title=wrapped_title,
                  labels={'id': 'Id of the vehicles', 'diff': 'Difference in seconds'}
                  )
    # Update trace labels based on the traffic type
    unit = '(s)' if traffic != 'routeLength' else '(m)'
    fig2.update_traces(texttemplate=f'%{{text}}{unit}', textposition='outside')

    # Update figure layout
    fig2.update_layout(yaxis=dict(categoryorder='total ascending'))
    fig2.update_layout(title={'y': 0.95, 'pad': {'b': 50}}, title_font_size=title_font_size)
    fig2.update_layout(template='plotly_dark', font=dict(color='#deb522'))

    return fig2
