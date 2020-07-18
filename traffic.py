#https://diegoquintanav.github.io/folium-barcelona-EN.html

import pandas as pd
from shapely.geometry import LineString
import matplotlib.pyplot as plt
import os
import folium
import branca
import os
import time
from selenium import webdriver
from datetime import date
import sys
from PIL import Image


import typing as T

from itertools import zip_longest
from geopandas import GeoDataFrame

DPI=300
title= "Barcelona traffic"
STREETS_MAPPING_URL='data/transit_relacio_trams.csv'
TRAMS_URL='data/2020_03_Marc_TRAMS_TRAMS.csv'

MAP_COORDS=[41.3947,2.1557]
MAP_ZOOM=12.5
MIN_HOUR=10
MAX_HOUR=22

def read_df():
    trf = pd.read_csv(TRAMS_URL, sep=",")
    trf['data_datetime'] = pd.to_datetime(trf["data"], format='%Y%m%d%H%M%S')

    return trf

# not tested
def reshape_line(line: T.List[str], chunksize: int, fillvalue: int) -> T.Iterable[T.Tuple[float]]:
    """Reshape a line to match the LineString WKT format
    
    This is based on `zip_longest`, read more in 
    <https://docs.python.org/3/library/itertools.html#itertools.zip_longest> and
    in the StackOverflow solution posted in <https://stackoverflow.com/a/434411/5819113>
    
    
        zip_longest('ABCD', 'xy', fillvalue='-') --> Ax By C- D-
       
    """
    args = [iter(float(el) for el in line)] * chunksize
    return zip_longest(*args, fillvalue=fillvalue)

def convert_line_to_wkt(line: str) -> LineString:
    splitted_line = line.split(",")
    reshaped_line = reshape_line(splitted_line, chunksize=2, fillvalue=None)
    return LineString(reshaped_line)


def generate_frames(trf):
    generate_frame_folium(trf)

def generate_frame_plot(trf):
    trf=filter_hours(trf,MIN_HOUR,MAX_HOUR)

    #Streets
    streets = pd.read_csv(STREETS_MAPPING_URL, sep=",")
    expanded_coords = streets["Coordenades"].str.split(",", expand=True)
    expanded_coords.head()

    coords_wkt = streets["Coordenades"].apply(lambda line: convert_line_to_wkt(line))


    crs = {'init': 'epsg:4326'}
    gdf = GeoDataFrame(streets, crs=crs, geometry=coords_wkt)
    ax = gdf.plot(cmap="YlOrRd")
    ax.set_title(title, fontdict={'fontsize': 20}, loc='center')
    ax.set_axis_off()

    plt.savefig(f'tmp/traffic.png', format='png', bbox_inches='tight', dpi=DPI)

def filter_hours(trf,min_hour,max_hour):
    return merged_gdf[(merged_gdf["data_datetime"].dt.hour > min_hour) & (merged_gdf["data_datetime"].dt.hour < max_hour)]

def style_function(feature):
    estat_actual = float(feature['properties']['estatActual'])
    return {
        'alpha': 0.5,
        'weight': 3,
        'color': '#black' if estat_actual is None else colorscale(estat_actual)
    }

def generate_frame_folium(trf):
    #Streets
    merged_gdf=merge_streets(trf)    

    #First weeek
    path1='tmp/img1.png'
    df1 = merged_gdf[(merged_gdf["data_datetime"].dt.date > date(2020,3,9)) & (merged_gdf["data_datetime"].dt.date  < date(2020,3,12))]
    df1 = df1.drop(columns="data_datetime", inplace=False)
    vmin,vmax = plot_folium_into_file(df1,path1)

    #Second weeek
    path2='tmp/img2.png'
    df2 = merged_gdf[(merged_gdf["data_datetime"].dt.date > date(2020,3,16)) & (merged_gdf["data_datetime"].dt.date  < date(2020,3,19))]
    df2 = df2.drop(columns="data_datetime", inplace=False)
    plot_folium_into_file(df2,path2,vmin,vmax)

    final_path='tmp/traffic_weekly.png'
    join_images([path1,path2],final_path)


def join_images(images,final_path):    
    images = [Image.open(x) for x in images]
    widths, heights = zip(*(i.size for i in images))

    total_width = sum(widths)
    max_height = max(heights)

    new_im = Image.new('RGB', (total_width, max_height))

    x_offset = 0
    for im in images:
        new_im.paste(im, (x_offset,0))
        x_offset += im.size[0]
    
    new_im.save(final_path)

def merge_streets(trf):
    streets = pd.read_csv(STREETS_MAPPING_URL, sep=",")
    expanded_coords = streets["Coordenades"].str.split(",", expand=True)

    coords_wkt = streets["Coordenades"].apply(lambda line: convert_line_to_wkt(line))

    crs = {'init': 'epsg:4326'}
    gdf = GeoDataFrame(streets, crs=crs, geometry=coords_wkt)

    coords_wkt = streets["Coordenades"].apply(lambda line: convert_line_to_wkt(line))

    _trf_to_merge = trf.copy()
    _streets_to_merge = streets.copy()
    # merge both dataframes using the id of the tram as common column
    _merged = _trf_to_merge.merge(_streets_to_merge, left_on="idTram", right_on="Tram")
    # drop unnecesary columns and set the idTram
    _merged = _merged.drop(columns=["data", "Tram", "Coordenades"], errors='ignore')

    crs = {'init': 'epsg:4326'}
    return GeoDataFrame(_merged, crs=crs, geometry=_merged['geometry'])

   

def plot_folium_into_file(df,filename,vmin=None,vmax=None):
    # plot the map
    df=merge_streets(df.groupby('idTram').agg({
        'estatActual':'mean'
    }).reset_index())
    print(df.head())

    if vmin is None or vmax is None:
        vmin=df['estatActual'].values.min()
        vmax=df['estatActual'].values.max()

    global colorscale
    colorscale = branca.colormap.linear.viridis.scale(vmin,vmax)
    colorscale.caption="Tram usage level"

    barca_map_colors = folium.Map(MAP_COORDS, zoom_start=MAP_ZOOM, tiles='cartodbpositron',zoom_control=False)

    (
        folium.GeoJson(
            df,
            style_function=style_function)
        .add_to(barca_map_colors)
    )


    # add legend, see <https://github.com/python-visualization/folium/issues/528>
    barca_map_colors.add_child(colorscale)

    # plot map
    path='tmp/traffic.html'
    barca_map_colors.save(path)
    save_folium_image(path,filename)
    return vmin,vmax
    

def main():
    # define default size of plots
    plt.rcParams["figure.figsize"] = (20,3)

    trf=read_df()
    trf.to_csv('tmp/traffic_data.csv')
    generate_frames(trf)

def save_folium_image(fn,name):
    delay=5
    tmpurl='file://{path}/{mapfile}'.format(path=os.getcwd(),mapfile=fn)

    browser = webdriver.Firefox()
    browser.get(tmpurl)
    #Give the map tiles some time to load
    time.sleep(delay)
    browser.save_screenshot(name)
    browser.quit()


if __name__ == "__main__":
    main()