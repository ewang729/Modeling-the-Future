import pandas as pd
import numpy
import pandas_profiling as pp
import geopandas as gpd
from shapely.geometry import Point, Polygon
import matplotlib.pyplot as plt
import matplotlib

matplotlib.use('TkAgg')

#df = pd.read_csv('resultphyschem.csv', converters={i: str for i in range(100)})
df = pd.read_csv('Arizona_pH_2010-2022_Result_Cleaned.csv',
usecols=['ActivityMediaSubdivisionName','ActivityStartDate','MonitoringLocationIdentifier',
'ActivityLocation/LatitudeMeasure', 'ActivityLocation/LongitudeMeasure', 'CharacteristicName', 'ResultMeasureValue'])
df = df.sort_values(by=['MonitoringLocationIdentifier', 'ActivityStartDate'], ascending=[True, True])
df = df[(df['CharacteristicName'] == 'pH')]
print(df)
#df.to_csv('Arizona_pH_LS_2020-2022.csv')

pd.to_numeric(df['ResultMeasureValue'])

#report = pp.ProfileReport(df)
#report.to_file('profile_report.html')

print('filtered')

az_map = gpd.read_file('tl_2016_04_cousub.shp')
geometry = [Point(xy) for xy in zip(df['ActivityLocation/LongitudeMeasure'], df['ActivityLocation/LatitudeMeasure'])]
geo_df = gpd.GeoDataFrame(df, geometry = geometry)
fig, ax = plt.subplots(1, 1, figsize = (15, 15))
az_map.plot(ax = ax, alpha = 0.4, color = 'grey')
geo_df.plot(column = 'ResultMeasureValue', ax=ax, cmap = 'hot', legend = True)
plt.title('Water pH in Arizona')
plt.xlim(-115, -110)
plt.ylim(30, 40)
plt.show()

