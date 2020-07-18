# https://diegoquintanav.github.io/folium-barcelona-EN.html
# https://towardsdatascience.com/visualizing-air-pollution-with-folium-maps-4ce1a1880677
# https://medium.com/@lyric09220/how-to-create-a-cool-seismic-heat-map-with-20-lines-of-python-code-e9b4bd9bc0b2


import pandas as pd
from shapely.geometry import LineString
import matplotlib.pyplot as plt
import matplotlib as mpl
import os
import numpy as np
import folium
import branca
import os
import time
from selenium import webdriver
from datetime import date
import sys
from PIL import Image
from folium.plugins import HeatMap


import typing as T

from itertools import zip_longest
from geopandas import GeoDataFrame

DPI=300
title= "Barcelona pollution"
PREV_FILE='data/aire/2020_02_Febrer_qualitat_aire_BCN.csv'
QUALITY_FILE='data/aire/Qualitat_Aire_Detall.csv'
CONTAMINANTS_FILE='data/aire/Qualitat_Aire_Contaminants.csv'
ESTACIONS_FILE='data/aire/Qualitat_Aire_Estacions.csv'
CONTAMINANTS=[
    "SO2",
    "NO",
    "NO2",
    "NOx",
    "O3",
    "CO",
    "PM10",
]

MAP_COORDS=[41.3947,2.1557]
MAP_ZOOM=12.5
MIN_HOUR=10
MAX_HOUR=22
HOURS_COLS=[ 'H{:>02d}'.format(x) for x in range(1,25)]
MIN_PREV_DAY=19
MAX_PREV_DAY=22
MIN_NOW_DAY=18
MAX_NOW_DAY=21
DRAW_DATA=True
BAR_PLOT=True

Y_LABEL={
    "SO2":"µg/m³",
    "NO":"µg/m³",
    "NO2":"µg/m³",
    "NOx":"µg/m³",
    "O3":"µg/m³",
    "CO":"mg/m³",
    "PM10":"µg/m³",
}

def read_df():
    qdf = pd.read_csv(QUALITY_FILE, sep=",")
    cdf = pd.read_csv(CONTAMINANTS_FILE, sep=",")
    edf = pd.read_csv(ESTACIONS_FILE, sep=",")


    df = qdf.merge(cdf, left_on="CODI_CONTAMINANT", right_on="Codi_Contaminant")
    df = df.merge(edf, left_on="ESTACIO", right_on="Estacio")

    return df

def get_stations_df():
    return pd.read_csv(ESTACIONS_FILE, sep=",").drop_duplicates(subset="Estacio")[['Estacio','nom_cabina','Latitud','Longitud']]

def read_prev_df():
    qdf = pd.read_csv(PREV_FILE, sep=",")
    cdf = pd.read_csv(CONTAMINANTS_FILE, sep=",")
    edf = pd.read_csv(ESTACIONS_FILE, sep=",")

    df = qdf.merge(cdf, left_on="CODI_CONTAMINANT", right_on="Codi_Contaminant")
    df = df.merge(edf, left_on="ESTACIO", right_on="Estacio")

    df=df[df['DIA'] > MIN_PREV_DAY]
    df=df[df['DIA'] < MAX_PREV_DAY]

    return df

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


def generate_frames(trf,contaminant,vmin=None,vmax=None,label='base'):
    return generate_frame_folium(trf,contaminant,vmin,vmax,label)


def filter_hours(trf,min_hour,max_hour):
    return merged_gdf[(merged_gdf["data_datetime"].dt.hour > min_hour) & (merged_gdf["data_datetime"].dt.hour < max_hour)]

def generate_frame_folium(df,contaminant,vmin,vmax,label):
    #First weeek
    base_path='tmp/pollution'
    os.makedirs(base_path,exist_ok=True)
    path1=f'{base_path}/pimg-{label}-{contaminant}.png'
    return plot_folium_into_file(df,contaminant,path1,vmin,vmax)

def filter_contaminant(df,contaminant):
    return df[df['Desc_Contaminant']==contaminant]

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


def plot_folium_into_file(df,contaminant,filename,vmin=None,vmax=None):
  
        
    steps=8
    colors=['Navy','Blue','Green','Yellow','Red']
    colorscale = branca.colormap.LinearColormap(colors=colors,vmin=vmin,vmax=vmax).to_step(steps)
    colorscale.caption=f"{contaminant} level"

    gradient_map={}
    for i,color in enumerate(colorscale.colors):
        print(color)
        step=1/steps*(i+1) 
        r =int(color[0]*255)
        g =int(color[1]*255)
        b =int(color[2]*255)
        gradient_map[step] = '#{:02x}{:02x}{:02x}'.format(r,g,b)
    print(gradient_map)

    df['nvalue'] = df['value'].subtract(vmin).fillna(0)
    print(df[['Latitud','Longitud','nvalue','value']].head(n=10))
    data1 = df[['Latitud','Longitud','nvalue']].values
    data_lab = df[['Latitud','Longitud','value','nvalue']].values

    map_osm = folium.Map(MAP_COORDS, zoom_start=MAP_ZOOM, tiles='cartodbpositron',zoom_control=False)
    hm=HeatMap(data1,gradient={0.4: 'blue', 0.95: 'lime', 1: 'red'})
    print(hm.options)
    hm.add_to(map_osm)

    if DRAW_DATA:
        for lat,lon,value,nvalue in data_lab:
            folium.Marker(location=[lat,lon],
                    icon=folium.DivIcon(html="""<div style="font-weight:bold">{:.2f}-{:.2f}</div>""".format(value,nvalue))
                    ).add_to(map_osm)


    # add legend, see <https://github.com/python-visualization/folium/issues/528>
    map_osm.add_child(colorscale)

    # plot map
    path='tmp/pollution.html'
    map_osm.save(path)
    save_folium_image(path,filename)
    return vmin,vmax

def groupby_df(df):
    args = {
        'Latitud':'first',
        'Longitud':'first'
    }
    for col in HOURS_COLS:
        args[col] = 'mean'
    df1=df.groupby('ESTACIO').agg(args).reset_index()


    df1['value']=0
    for col in HOURS_COLS:
        df1['value'] = df1['value'] + df1[col]
    df1['value']=df1['value'].divide(len(HOURS_COLS))
    return df1

def get_min_max_values(df,contaminant):
    dff=df['value'].dropna()
    vmin=dff.min()
    vmax=dff.max()
    return vmin,vmax


def main_folium():
    # define default size of plots
    plt.rcParams["figure.figsize"] = (20,3)    

    for contaminant in CONTAMINANTS:
        print(f" analitzant contaminant {contaminant}")
        df1=read_df()
        dfg1=filter_contaminant(df1,contaminant)
        dfg1=groupby_df(dfg1)
        vmin1,vmax1=get_min_max_values(dfg1,contaminant)

        df2=read_prev_df()
        dfg2=filter_contaminant(df2,contaminant)
        dfg2=groupby_df(dfg2)
        vmin2,vmax2=get_min_max_values(dfg2,contaminant)

        vmin=min(vmin1,vmin2)
        vmax=max(vmax1,vmax2)

        print(f'vmin1: {vmin1}, vmax1: {vmax1}')
        print(f'vmin2: {vmin2}, vmax2: {vmax2}')
        print(f'min: {vmin}, max: {vmax}')

        fdf2=add_zero_df(dfg2,dfg1)
        generate_frames(fdf2,contaminant,vmin,vmax,'prev')

        fdf1=add_zero_df(dfg1,dfg2)
        generate_frames(fdf1,contaminant,vmin,vmax)

        join_images([
            f'tmp/pollution/pimg-prev-{contaminant}.png',
            f'tmp/pollution/pimg-base-{contaminant}.png'
        ],f'tmp/pollution/pollution-{contaminant}.png')
            

def save_folium_image(fn,name):
    delay=5
    tmpurl='file://{path}/{mapfile}'.format(path=os.getcwd(),mapfile=fn)

    browser = webdriver.Firefox()
    browser.get(tmpurl)
    #Give the map tiles some time to load
    time.sleep(delay)
    browser.save_screenshot(name)
    browser.quit()

def add_zero_df(df,zdf):
    dd = zdf.copy()
    dd[['Latitud','Longitud']]=dd[['Latitud','Longitud']].subtract(10)

    return pd.concat([df,dd])

def main_bar_plot():
    dfnow=read_df()
    dfpre=read_prev_df()

    sdf=get_stations_df()
    for contaminant in CONTAMINANTS:
        print(f" analitzant contaminant {contaminant}")

        #now data
        dfgnow=filter_contaminant(dfnow,contaminant)
        dfgnow=groupby_df(dfgnow)

        key=f'{contaminant}.now'
        dfgnow = dfgnow.rename(columns={
            'value':key
        })

        sdf = sdf.merge(dfgnow[['ESTACIO',key]], left_on="Estacio", right_on="ESTACIO").drop(columns=['ESTACIO'])


        #pre data
        dfgpre=filter_contaminant(dfpre,contaminant)
        dfgpre=groupby_df(dfgpre)

        key=f'{contaminant}.pre'
        dfgpre = dfgpre.rename(columns={
            'value':key
        })

        sdf = sdf.merge(dfgpre[['ESTACIO',key]], left_on="Estacio", right_on="ESTACIO").drop(columns=['ESTACIO'])

    print(sdf.head())

    path='tmp/pollution/figs'
    os.makedirs(path,exist_ok=True)
    sdf.to_csv(f'{path}/data.csv')

    legend=[
        f'2020/02/{MIN_PREV_DAY} - 2020/02/{MAX_PREV_DAY}',
        f'2020/03/{MIN_NOW_DAY} - 2020/03/{MAX_NOW_DAY}',
    ]
    for contaminant in CONTAMINANTS:
        pkey=f'{contaminant}.pre'
        nkey=f'{contaminant}.now'
        ax=sdf.plot(kind='bar',x='nom_cabina',y=[pkey,nkey], rot=30)
        ax.set_xlabel("Station")
        ax.set_ylabel(f'{contaminant} ({Y_LABEL[contaminant]})')
        plt.title(f'{contaminant} levels')
        plt.legend(legend)
        plt.tight_layout()

        plt.savefig(f'{path}/{contaminant}.png',dpi=300)

if __name__ == "__main__":
    if BAR_PLOT:
        main_bar_plot()
    else:
        main_folium()