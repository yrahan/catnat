import pandas as pd
import numpy as np

import glob
import os

import requests

import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px

import zipfile

import xarray as xr

import folium
from folium.plugins import MarkerCluster

import pandas as pd
from geopy.geocoders import Nominatim

import geopandas as gpd
import cartopy.crs as ccrs

import imageio

from sklearn.neighbors import KDTree
from sklearn.neighbors import BallTree

from sklearn.preprocessing import RobustScaler

# Importing Required Libraries
import panel as pn
import pandas as pd
import plotly.express as px



decree_filename_base = 'arrete_'
decrees_folder_name = './../../data/raw/decrees'
communes_folder_name = './../../data/raw/opendatasoft'
weather_folder_name = './../../data/raw/weather/era5'
weather_ncfiles_folder_name = './../../data/raw/weather/era5/ncfiles2'
processed_data_folder_name = './../../data/processed'
output_data_folder_name = './../../data/processed/output'
decrees_filename = 'decrees.parquet'
decrees_locations_filename = 'decrees_locations.parquet'
communes_csv_filename = 'correspondance-code-insee-code-postal-202410.csv'
weather_filename = 'weather2.parquet'
weather_shema_filename = 'weather_shema2.csv'
weather_yearly_filename = 'weather2_yearly.parquet'
weather_yearly_shema_filename = 'weather_shema2_yearly.csv'
drought_filename = 'drought.parquet'
drought_shema_filename = 'drought_shema.csv'
drought_yearly_filename = 'drought_yearly.parquet'
drought_yearly_shema_filename = 'drought_yearly_shema.csv'
drought_commune_clean_filename = 'drought_commune_clean.parquet'
drought_commune_clean_shema_filename = 'drought_commune_clean_shema.csv'
drought_weather_filename = 'drought_weather.parquet'
drought_weather_shema_filename = 'drought_weather_shema.csv'
#weather_zip_file = "193fcd51a8958175843ecbbcaba057c8.zip"


# Enable Panel's extensions
pn.extension('plotly')



# read the dataframe from parquet
df = pd.read_parquet(os.path.join(processed_data_folder_name, drought_weather_filename))
# Load the schema (data types) from the file
schema = pd.read_csv(os.path.join(processed_data_folder_name, drought_weather_shema_filename), index_col=0).squeeze("columns")
# Apply the schema to the loaded dataframe
df = df.astype(schema.to_dict())
df_applied_ori = df.copy()
# Remove rows where applied_1 is equal to 0
df = df[df['applied_1'] != 0]
df_applied_ori = df.copy()


# Filter out communes with drought declarations (decision_1 = 1)
df_drought = df[df['decision_1'] == 1]

##df = pd.DataFrame(data)
#################################################################

# Importing Required Libraries
import panel as pn
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import folium
from folium.plugins import HeatMap
import branca.colormap as cm

# Enable Panel's extensions
pn.extension('plotly')

# Load the Dataset (assuming CSV file)
# df = pd.read_csv('french_communes_weather.csv')

# Sample DataFrame for illustrative purposes
# data = {
#     'year_1': [2018, 2018, 2019, 2019, 2019, 2020, 2020, 2021],
#     'insee_1': ['12345', '67890', '12345', '67890', '54321', '67890', '12345', '54321'],
#     'decision_1': [1, 0, 1, 1, 1, 0, 1, 1],
#     'latitude_1': [46.5, 48.8, 46.5, 48.8, 45.3, 48.8, 46.5, 45.3],
#     'longitude_1': [2.5, 2.3, 2.5, 2.3, 4.8, 2.3, 2.5, 4.8]
# }
# df = pd.DataFrame(data)

# Filter the DataFrame to include only communes with drought declarations
df_drought = df[df['decision_1'] == 1]

# Count the number of communes per year_1 with drought declarations
communes_per_year = df_drought.groupby('year_1')['insee_1'].nunique().reset_index()
communes_per_year.columns = ['Year', 'Number of Communes with Drought']

# Create a base line chart using Plotly
fig = px.line(
    communes_per_year,
    x='Year',
    y='Number of Communes with Drought',
    title="Number of Communes with Drought Declarations per Year",
    labels={'Year': 'Year', 'Number of Communes with Drought': 'Number of Communes'},
    markers=True
)

# Add a vertical line initially at the first year
vertical_line = go.layout.Shape(
    type='line',
    x0=communes_per_year['Year'].min(),
    y0=0,
    x1=communes_per_year['Year'].min(),
    y1=communes_per_year['Number of Communes with Drought'].max(),
    line=dict(color='Red', dash='dot'),
    name='Selected Year'
)
fig.add_shape(vertical_line)

# Create a Map of France with Drought Locations
slider = pn.widgets.IntSlider(name='Year Slider', start=df['year_1'].min(), end=df['year_1'].max(), step=1, value=df['year_1'].min())

@pn.depends(slider.param.value)
def update_map(year):
    # Filter data for selected year
    df_selected_year = df[(df['year_1'] == year) & (df['decision_1'] == 1)]

    # Create a map centered around France
    m = folium.Map(location=[46.603354, 1.888334], zoom_start=5)

    # Add drought points as a heatmap to the map
    heat_data = [[row['latitude_1'], row['longitude_1']] for idx, row in df_selected_year.iterrows()]
    heatmap = HeatMap(heat_data, min_opacity=0.2, max_zoom=13, radius=15, blur=10)
    heatmap.add_to(m)

    # Add a color bar to the map
    colormap = cm.LinearColormap(colors=['blue', 'green', 'yellow', 'red'], vmin=0, vmax=1, caption='Drought Intensity')
    colormap.add_to(m)

    return m

map_view = pn.pane.HTML(height=600, width=800, sizing_mode='fixed')

def update_map_view(event):
    year = slider.value
    folium_map = update_map(year)
    map_view.object = folium_map._repr_html_()

slider.param.watch(update_map_view, 'value')
update_map_view(None)  # Initialize with the first map

@pn.depends(slider.param.value)
def update_line_chart(year):
    # Update the vertical line in the plot
    fig_updated = go.Figure(fig)
    fig_updated.update_shapes(dict(
        x0=year,
        x1=year,
        y0=0,
        y1=communes_per_year['Number of Communes with Drought'].max(),
        line=dict(color='Red', dash='dot')
    ))
    return fig_updated

# Create a layout for the map and line chart to ensure proper spacing and layout
layout = pn.Column(
    "# Interactive Map and Analysis of Drought in French Communes",
    pn.Row(
        map_view,
        sizing_mode='fixed',
        width_policy='max',
        margin=(0, 10, 20, 10)
    ),
    pn.Spacer(height=20),
    slider,  # Place the slider directly below the map
    pn.Spacer(height=20),
    "# Drought Declarations per Year in French Communes",
    pn.Spacer(height=20),
    pn.panel(update_line_chart)
)

# Serve the Panel application
if __name__ == '__main__':
    layout.show(port=8061, allow_websocket_origin=['*'])
