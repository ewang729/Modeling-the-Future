import pandas as pd
from haversine import haversine
from datetime import date
import matplotlib.pyplot as plt
import matplotlib.dates as dates
import numpy as np

mine_file = "Morenci_Mine.csv"
water_file = "Arizona_pH.csv"

coords = (33.0635, -109.3353)

mine = pd.read_csv("cleaned data/" + mine_file)
water = pd.read_csv("cleaned data expanded/" + water_file)
water['date'] = pd.to_datetime(water['date'])
mine['date'] = pd.to_datetime(mine['date'])
mine = mine[mine['type'] == 'Total']

print(mine)
print(water)

best = 50000
location = ""

for row in water.itertuples():
	test = haversine(coords, (row.latitude, row.longitude))
	if test < best:
		best = test;
		location = row.loc

print("Nearest location: " + str(best))

nearest = water[water['loc'] == location]

def last_quarter(dt):
	year = dt.year
	month, day = 0, 0
	if dt.month < 4:
		month, day = 12, 31
		year = year - 1
	elif dt.month < 7:
		month, day = 3, 31
	elif dt.month < 10:
		month, day = 6, 30
	else:
		month, day = 9, 30
	return date(year, month, day)

minedict = {}
for row in mine.itertuples():
	minedict[row.date.date()] = row.hrs

x = []
y = []
z = []

for row in nearest.itertuples():
	last = last_quarter(row.date)
	if last.year < 1983:
		continue
	x.append(minedict[last])
	y.append(row.res)
	z.append(row.date)

dz = dates.date2num(z)

#plt.scatter(x, y, c = dz, cmap = 'hot')
plt.scatter(x, y)
plt.title('pH against Mine Activity')
plt.xlabel('Mine Activity (hours)')
plt.ylabel('water pH')
plt.show()

print("correlation against activity:")
print(np.corrcoef(x, y))
print("correlation against date:")
print(np.corrcoef(dz, y))
