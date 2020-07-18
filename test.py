
import os

import matplotlib.pyplot as plt
import pandas as pd
import geopandas as gpd


datafile = 'data/datatmp.csv'
shapefile = 'data/ne_10m_admin_0_countries.shp'

colors = 9
cmap = 'Blues'
figsize = (16, 10)
year = '2016'
cols = ['Country Name', 'Country Code', year]
title = 'Individuals using the Internet (% of population) in {}'.format(year)
imgfile = 'img/{}.png'.format(2)

description = '''
Individuals who have used the Internet from any location in the last 3 months via any device based on the International Telecommunication Union,
World Telecommunication/ICT Development Report and database. Data: World Bank - worldbank.org • Author: Ramiro Gómez - ramiro.org'''.strip()

gdf = gpd.read_file(shapefile)[['ADM0_A3', 'geometry']].to_crs('+proj=robin')
print("---> gdf")
print(gdf.head(20))

df = pd.read_csv(datafile)
print("\n---> df")
print(df.head(20))

merged = gdf.merge(df, left_on='ADM0_A3', right_on='Country Code',how='outer')
print("\n---> merged")
print(merged.head(20))
print("\n---> merged (dropna)")
print( merged.dropna().head(20))

ax = merged.dropna().plot(column=year, cmap=cmap, figsize=figsize, scheme='equal_interval', k=colors, legend=True)

nmerged = merged[merged.isna().any(axis=1)]
print("\n---> nmerged")
print(nmerged.head(20))
nmerged.plot(ax=ax, color='#fafafa', hatch='///')

ax.set_title(title, fontdict={'fontsize': 20}, loc='left')
ax.annotate(description, xy=(0.1, 0.1), size=12, xycoords='figure fraction')

ax.set_axis_off()
ax.set_xlim([-1.5e7, 1.7e7])
ax.get_legend().set_bbox_to_anchor((.12, .4))
ax.get_figure()
plt.savefig('tmp/test.png')