import folium
import numpy as np
import os
import pandas as pd
import geopandas as gpd
import matplotlib as mpl
from matplotlib import pyplot as plt
import matplotlib.colors as colors
from datetime import datetime

JOIN_COL='SUBUNIT'
BACKGROUND_COLOR="#FFF"
CMAP = 'YlOrRd'
COLORS = 9
EDGE_COLOR='#9B9B9B'
NON_REGION_COLOR='#DDD'
DPI=110

SIZE=(
   19,
   12     
)

def get_gdf():
    shapefile = 'data/world/ne_10m_admin_0_countries_lakes.shp'
    gdf = gpd.read_file(shapefile)[['ADM0_A3', 'geometry',JOIN_COL]].to_crs('+proj=robin')
    gpd.read_file(shapefile).drop(columns=['geometry']).to_csv('tmp/gdf.csv')
    return gdf

def get_ccaa_gdf():
    shapefile = 'data/ccaa/comunidades-autonomas-espanolas.geojson'
    gdf =  gpd.read_file(shapefile)
    print(gdf.head())
    gdf =gdf[['geometry','texto','codigo']].to_crs('+proj=robin')
    gdf['codigo']=gdf['codigo'].astype(str).astype(int)
    #gdf=gdf.drop(3)
    gpd.read_file(shapefile).drop(columns=['geometry']).to_csv('tmp/gdf.csv')
    return gdf


#https://ramiro.org/notebook/geopandas-choropleth/save_date
def generate_frame(df,date,vmin,vmax,gdf,left_on,right_on,figsize,label,title):
    plt.rcParams['axes.facecolor']=BACKGROUND_COLOR
    plt.rcParams['savefig.facecolor']=BACKGROUND_COLOR

  

    merged = gdf.merge(df, left_on=left_on, right_on=right_on,how='outer')
    print(f"\n---> date: {date}")
    print(merged.dropna().head(20))

    norm = mpl.colors.LogNorm(vmin=vmin, vmax=vmax)
    cmap = mpl.cm.ScalarMappable(norm=norm, cmap=CMAP).cmap

    if merged.dropna().empty:
        print("df is empty")
        return

    ax = merged.dropna().plot(column='value',cmap=cmap,norm=norm, figsize=figsize,edgecolor = EDGE_COLOR,linewidth=0.5)
    nmerged = merged[merged.isna().any(axis=1)]

    nmerged.plot(ax=ax, facecolor=NON_REGION_COLOR)

    ax.set_title(title, fontdict={'fontsize': 20}, loc='center')

    ax.set_axis_off()
    #ax.set_xlim([-1.5e7, 1.7e7])

    plt.savefig(f'tmp/frames/frame{label}.png', format='png', bbox_inches='tight', dpi=DPI)

def generate_video_from_df(df):
    
    dates = df.index.tolist()
    df=df.T.drop("World")
    gdf = get_gdf()
    min_value = df.dropna().values.min()
    max_value = df.dropna().values.max()
    print(f"min: {min_value}, max: {max_value}")

    for date in dates:
        title = 'Coronavirus cases on {}'.format(date)
        generate_frame(get_date_df(df,date),date,min_value,max_value,gdf,JOIN_COL,'Country Code',SIZE,date,title)


def generate_deaths_video_from_df(df):    
    dates = df.index.tolist()
    df=df.T.drop("World")
    gdf = get_gdf()
    print(df.sample(n=10))

    valdf=df.fillna(1)
    min_value = valdf.values.min()
    max_value = valdf.values.max()
    print(f"min: {min_value}, max: {max_value}")

    for date in dates:
        title = 'Coronavirus deaths on {}'.format(date)
        generate_frame(get_date_df(df,date),date,min_value,max_value,gdf,JOIN_COL,'Country Code',SIZE,date,title)
    

def get_date_df(df,date):
    df=pd.DataFrame(df[date]).reset_index().rename(columns={date:'value','index':'Country Code'})
    return df

def get_ccaa_date_df(df,date):
    df=pd.DataFrame(df[['cod_ine',date]]).reset_index().rename(columns={date:'value'})
    return df

# https://www.google.com/search?client=ubuntu&channel=fs&q=geopandas+plot+size+to+small&ie=utf-8&oe=utf-8
def generate_ccaa_video_from_df(df):
    df=df.drop(columns=['CCAA'])
    dates = df.columns.tolist()[1:]
    dates.sort()
    odata=df.dropna()
    min_value = max(odata.values.min(),1)
    max_value = odata.values.max()
    print(f"min: {min_value}, max: {max_value}")
    

    gdf = get_ccaa_gdf()

    for date in dates:
        label=format_date(date)
        generate_frame(get_ccaa_date_df(df,date),date,min_value,max_value,gdf,'codigo','cod_ine',SIZE,label)


def format_date(date):
    return datetime.strptime(date,'%d/%m/%Y').strftime('%y-%m-%d')

