# Import required libraries
import pandas as pd
import numpy as np
import plotly.express as px
import dash
from dash import Dash, dcc, html, Input, Output

# Obsolete imports:
# import dash_html_components as html
# import dash_core_components as dcc
# from dash.dependencies import Input, Output


# Read the airline data into pandas dataframe
spacex_df = pd.read_csv('spacex_launch_dash.csv')
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Variables needed for the functions
total = spacex_df['class'].sum()
filtered_df = spacex_df[['Launch Site','class']]
groupby_sum_df = filtered_df.groupby('Launch Site')['class'].sum()
groupby_count_df = filtered_df.groupby('Launch Site')['class'].count()
all_data = (groupby_sum_df/total).reset_index()
sites = ['site1', 'site2', 'site3', 'site4']
dict_names = dict(zip(all_data['Launch Site'].tolist(),sites))
dict_inv = {v: k for k, v in dict_names.items()}
each_data = (groupby_sum_df/groupby_count_df).to_frame()
each_data['failures'] = 1-each_data['class']
each_data = each_data.rename(index=dict_names).T
each_data['labels'] = [1,0]
range_marks = pd.Series(np.arange(0,11000,1000))
dict_marks = dict(zip(range_marks,range_marks.map(lambda x: str(x))))

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1(
        'SpaceX Launch Records Dashboard',
        style={
            'textAlign': 'center', 
            'color': '#503D36', 
            'font-size': 40
        }
    ),
    
    # TASK 1: Add a dropdown list to enable Launch Site selection
    # The default select value is for ALL sites
    dcc.Dropdown(
        id='site-dropdown',
        options=[
            {'label': 'All Sites'   , 'value': 'ALL'  },
            {'label': 'CCAFS LC-40' , 'value': 'site1'},
            {'label': 'CCAFS SLC-40', 'value': 'site2'},
            {'label': 'KSC LC-39A'  , 'value': 'site3'},
            {'label': 'VAFB SLC-4E' , 'value': 'site4'}
        ],
        value='ALL',
        placeholder='Select a Launch Site here',
        searchable=True
    ),
    html.Br(),
    
    # TASK 2: Add a pie chart to show the total successful launches count for all sites
    # If a specific launch site was selected, show the Success vs. Failed counts for the site
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),
    
    # TASK 3: Add a slider to select payload range
    html.P('Payload range (kg):'),
    dcc.RangeSlider(
        id='payload-slider', min=0, max=10000, step=1000, 
        marks=dict_marks, value=[min_payload, max_payload]
    ),

    # TASK 4: Add a scatter chart to show the correlation between payload and launch success
    html.Div(dcc.Graph(id='success-payload-scatter-chart'))
])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
# Function decorator to specify function input and output
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site): 
    if entered_site == 'ALL':
        fig = px.pie(
            data_frame=all_data, 
            values='class', 
            names='Launch Site', 
            title='Total Success Launches by Site'
        )
    else:
        for site in sites:
            if entered_site == site:
                site_name = str(pd.Series(site).map(dict_inv)[0])
                fig = px.pie(
                    data_frame=each_data, 
                    values=site, 
                    names='labels', 
                    title='Total Success Launches for Site ' + site_name
                )
    return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, 
# `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def get_scatter(entered_site,payload_range):
    if entered_site == 'ALL':
        fig = px.scatter(
            data_frame=spacex_df,
            x='Payload Mass (kg)', y='class', color='Booster Version Category', 
            title='Correlation between Payload and Success for all Sites',
            range_x=payload_range, range_y=(-1,2)
        )
    else:
        for site in sites:
            if entered_site == site:
                site_name = str(pd.Series(site).map(dict_inv)[0])
                fig = px.scatter(
                    data_frame=spacex_df[spacex_df['Launch Site']==site_name],
                    x='Payload Mass (kg)', y='class', color='Booster Version Category',
                    title='Correlation between Payload and Success for Site ' + site_name,
                    range_x=payload_range, range_y=(-1,2)
                )
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server()
