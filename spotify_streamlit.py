import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

# get csv data
all_df = pd.read_csv('combined_top_tracks.csv')
my_df = pd.read_csv('my_top_100_tracks.csv')
usa_df = pd.read_csv('usa_top_50_tracks.csv')
global_df = pd.read_csv('global_top_50_tracks.csv')

# init state
if 'option' not in st.session_state:
    st.session_state.option = 'All Tracks'
if 'metric' not in st.session_state:
    st.session_state.metric = 'popularity'
if 'metric_2' not in st.session_state:
    st.session_state.metric_2 = 'danceability'
if 'chart_type' not in st.session_state:
    st.session_state.chart_type = 'Bar Chart'
if 'df' not in st.session_state:
    st.session_state.df = all_df

def set_option(option):
    st.session_state.option = option

# map options to dataframes
df_mapping = {
    'All Tracks': all_df,
    'My Tracks': my_df,
    'USA Tracks': usa_df,
    'Global Tracks': global_df
}

# title and logo
with st.container():
    col1, col2 = st.columns([0.1, 0.1])
    with col1:
        st.title("Spotify Song Finder EDA Tool")
    with col2:
        st.image("Spotify_Primary_Logo_RGB_Green-300x300.png", width=100)

def get_metric_summary(df, metric):
    """Get formatted summary statistics based on metric type"""
    stats = {
        'popularity': {
            'format': '.0f',
            'stats': ['mean', 'median', 'min', 'max']
        },
        'loudness': {
            'format': '.1f',
            'stats': ['mean', 'median', 'min', 'max']
        },
        'danceability': {
            'format': '.3f',
            'stats': ['mean', 'median', 'min', 'max']
        },
        'energy': {
            'format': '.3f',
            'stats': ['mean', 'median', 'min', 'max']
        },
        'speechiness': {
            'format': '.3f',
            'stats': ['mean', 'median', 'min', 'max']
        },
        'acousticness': {
            'format': '.3f',
            'stats': ['mean', 'median', 'min', 'max']
        },
        'instrumentalness': {
            'format': '.3f',
            'stats': ['mean', 'median', 'min', 'max']
        },
        'liveness': {
            'format': '.3f',
            'stats': ['mean', 'median', 'min', 'max']
        },
        'valence': {
            'format': '.3f',
            'stats': ['mean', 'median', 'min', 'max']
        }
    }
    
    metric_config = stats.get(metric, {
        'format': '.3f',
        'stats': ['mean', 'median', 'min', 'max']
    })
    format_str = metric_config['format']
    
    summary = {}
    for stat in metric_config['stats']:
        if stat == 'mean':
            value = df[metric].mean()
        elif stat == 'median':
            value = df[metric].median()
        elif stat == 'min':
            value = df[metric].min()
        elif stat == 'max':
            value = df[metric].max()
            
        summary[stat] = f"{value:{format_str}}"
    
    return summary

def update_metric():
    st.session_state.metric = st.session_state.temp_metric

def update_metric_2():
    st.session_state.metric_2 = st.session_state.temp_metric_2

def update_chart_type():
    st.session_state.chart_type = st.session_state.temp_chart_type
    # Initialize second metric when switching to scatter plot
    if st.session_state.chart_type == 'Scatter Plot' and 'metric_2' not in st.session_state:
        # Set default second metric to first available option that's not the current metric
        available_metrics = [opt for opt in plot_options]
        st.session_state.metric_2 = available_metrics[0]

with st.expander("Filter Tracks"):
    selected_option = st.pills(
        options=["All Tracks", "My Tracks", "USA Tracks", "Global Tracks"],
        label="Filter Tracks"
    )
    
    # update session state only if we got a valid selection
    if selected_option is not None:
        set_option(selected_option)

with st.sidebar:
    # add summary statistics before plot options
    st.write(f"### {st.session_state.option} - Summary Statistics")
    current_df = df_mapping[st.session_state.option]
    
    if st.session_state.chart_type == 'Scatter Plot':
        # for scatter plots, show stats for both metrics
        col1, col2 = st.columns(2)
        with col1:
            stats1 = get_metric_summary(current_df, st.session_state.metric)
            st.write(f"**{st.session_state.metric}**")
            for stat, value in stats1.items():
                st.write(f"{stat.title()}: {value}")
        with col2:
            stats2 = get_metric_summary(current_df, st.session_state.metric_2)
            st.write(f"**{st.session_state.metric_2}**")
            for stat, value in stats2.items():
                st.write(f"{stat.title()}: {value}")
    else:
        # for other charts, show stats for single metric
        stats = get_metric_summary(current_df, st.session_state.metric)
        st.write(f"**{st.session_state.metric}**")
        for stat, value in stats.items():
            st.write(f"{stat.title()}: {value}")
    
    st.write("---")
    st.write("Plot Options")
    plot_options = ['popularity', 'danceability', 'energy', 'loudness', 'speechiness', 
                   'acousticness', 'instrumentalness', 'liveness', 'valence']
    
    # use callback to update the metric
    st.selectbox(
        "Select primary metric to plot",
        plot_options,
        key='temp_metric',
        on_change=update_metric
    )

    # use callback for second metric
    st.selectbox(
        "Select secondary metric for scatter plot", 
        [opt for opt in plot_options],
        key='temp_metric_2',
        on_change=update_metric_2,
        index=plot_options.index(st.session_state.metric_2) if 'metric_2' in st.session_state else 0,
        disabled=(st.session_state.chart_type == 'Bar Chart')
    )

    chart_types = ['Bar Chart', 'Scatter Plot']
    st.selectbox(
        "Select chart type",
        chart_types,
        key='temp_chart_type',
        on_change=update_chart_type
    )
        
    # add correlation matrix heatmap
    st.write(f"{st.session_state.option} - Correlation Matrix")
    corr_df = df_mapping[st.session_state.option][plot_options].corr()
    fig_corr = px.imshow(
            corr_df,
            color_continuous_scale='RdBu',
            aspect='auto',
        labels=dict(color="Correlation")
    )
    fig_corr.update_layout(height=400, width=400)
    st.plotly_chart(fig_corr, use_container_width=True)

# before using df_mapping, ensure we have a valid option
if st.session_state.option is None:
    st.session_state.option = "All Tracks"

# set y-axis range based on metric
range_mapping = {
    'popularity': [0, 100],
    'danceability': [0, 1],
    'energy': [0, 1], 
    'loudness': [-60, 0],
    'speechiness': [0, 1],
    'acousticness': [0, 1],
    'instrumentalness': [0, 1],
    'liveness': [0, 1],
    'valence': [0, 1],
}

y_range = range_mapping[st.session_state.metric]

def normalize_series(series):
    """Normalize a series to 0-1 range"""
    min_val = series.min()
    max_val = series.max()
    return (series - min_val) / (max_val - min_val)

def create_chart(df, chart_type, metric, y_range):
    if chart_type == 'Bar Chart':
        return px.bar(
            data_frame=df,
            x='name',
            y=metric,
            hover_data=['artists', metric],
            labels={'name': 'Track Name', 'popularity': 'Popularity', 'artists': 'Artists'},
            range_y=y_range,
            color_discrete_sequence=['rgba(29, 215, 84, 0.8)'],
            height=700
        )
    elif chart_type == 'Scatter Plot':
        # create a copy of the dataframe to avoid modifying original
        plot_df = df.copy()
        
        # normalize both metrics
        metric1_norm = normalize_series(plot_df[metric])
        metric2_norm = normalize_series(plot_df[st.session_state.metric_2])
        
        # add normalized columns with original values in hover data
        plot_df[f'{metric}_normalized'] = metric1_norm
        plot_df[f'{st.session_state.metric_2}_normalized'] = metric2_norm
        
        return px.scatter(
            data_frame=plot_df,
            x=f'{metric}_normalized',
            y=f'{st.session_state.metric_2}_normalized',
            hover_data=['name', 'artists', metric, st.session_state.metric_2],
            labels={
                'name': 'Track Name',
                f'{metric}_normalized': metric,
                f'{st.session_state.metric_2}_normalized': st.session_state.metric_2,
                'artists': 'Artists'
            },
            color_discrete_sequence=['rgba(29, 215, 84, 0.8)'],
            range_x=[0, 1],
            range_y=[0, 1],
            height=700
        )

# visualize track data
df = df_mapping[st.session_state.option]
fig = create_chart(df, st.session_state.chart_type, st.session_state.metric, y_range)
st.plotly_chart(fig, use_container_width=True)
