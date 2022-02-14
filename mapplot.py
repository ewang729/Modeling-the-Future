import pandas as pd
import numpy
import pandas_profiling as pp
import geopandas as gpd
from shapely.geometry import Point, Polygon
import matplotlib.pyplot as plt
import matplotlib

matplotlib.use('TkAgg')

df = pd.read_csv('slopes/Arizona_pH.csv', usecols=['latitude', 'longitude', 'res'])
print(df)

pd.to_numeric(df['res'])

print('filtered')

az_map = gpd.read_file('image files/Arizona/tl_2016_04_cousub.shp')
geometry = [Point(xy) for xy in zip(df['longitude'], df['latitude'])]
geo_df = gpd.GeoDataFrame(df, geometry = geometry)
fig, ax = plt.subplots(1, 1, figsize = (15, 15))
az_map.plot(ax = ax, alpha = 0.4, color = 'grey')
geo_df.plot(column = 'res', ax=ax, cmap = 'hot', legend = True)
plt.title('pH Change per Year in Arizona')
plt.xlim(-115, -108.5)
plt.ylim(30, 40)
plt.show()

