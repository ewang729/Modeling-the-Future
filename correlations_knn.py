import pandas as pd
from haversine import haversine
from datetime import date
import matplotlib.pyplot as plt
import matplotlib.dates as dates
import numpy as np
from sklearn.tree import DecisionTreeRegressor as dtr
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor as rfr
from sklearn import neighbors
from sklearn.linear_model import LinearRegression as lr
from lineartree import LinearTreeRegressor as ltr
from lineartree import LinearForestRegressor as lfr
from statistics import mean
from math import sqrt

mine_name = "Ray"
mine_file = mine_name + "_Mine.csv"
water_file = "Arizona_pH.csv"

coords_key = {"Morenci" : (33.0635, -109.3353), "Bagdad" : (34.5847, -113.2111), "Ray" : (33.1301, -110.9790)}
coords = coords_key[mine_name]

mine = pd.read_csv("cleaned data/" + mine_file)
water = pd.read_csv("cleaned data expanded/" + water_file)
water['date'] = pd.to_datetime(water['date'])
mine['date'] = pd.to_datetime(mine['date'])

print(mine)
print(water)

# function to convert date to integer
def to_int(dt):
	return 366 * dt.year + 31 * dt.month + dt.day

dist = {}  # distance from each location to mine
for row in water.itertuples():
	dist[row.loc] = haversine(coords, (row.latitude, row.longitude))

# generate set of unique locations
# locations are designated by distance to mine
locations = set()
locations_list = []
for row in water.itertuples():
	locations.add(dist[row.loc])
	locations_list.append(dist[row.loc])

# add distance to mine as a property
water['distance'] = locations_list

minedict = {}  # hours recorded for each quarter
for row in mine.itertuples():
	key = to_int(row.date)
	minedict[key] = [row.mining, row.plant, key]

tree = lfr(base_estimator = lr(), min_samples_split = 8)

correlations = []

# generate list of production quarters in range of years
md = [[3, 31], [6, 30], [9, 30], [12, 31]]
def quarters(start, end):
	qtrs = []
	qtrsd = []
	for i in range(start, end + 1):
		for j in range(0, 4):
			dt = date(i, md[j][0], md[j][1])
			if to_int(dt) in minedict:
				qtrs.append(to_int(dt))
				qtrsd.append(dt)
	return [qtrs, qtrsd]

for d in locations:
	current = water[water['distance'] == d]

	if d > 30:
		continue

	av = []

	for row in current.itertuples():
		av.append([to_int(row.date), row.date, row.res])

	av.sort()
	start_year = av[0][1].year
	end_year = av[-1][1].year
	qtrs, qtrsd = quarters(start_year, end_year)
	
	if len(qtrs) < 10 or len(av) < 10:
		continue

	x = []
	y = []
	z = []
	for i in range(0, len(av)):
		x.append(av[i][0])
		z.append(av[i][1])
		y.append(av[i][2])
	
	plt.scatter(z, y)

	x = np.array(x).reshape(-1, 1)
	qtrs = np.array(qtrs).reshape(-1, 1)
	knn = neighbors.KNeighborsRegressor(8, weights = 'uniform')
	y_ = knn.fit(x, y).predict(qtrs)
	
	x = qtrs
	y = y_
	plt.scatter(qtrsd, y)
	plt.title('pH against date')
	plt.xlabel('date')
	plt.ylabel('water pH')
	
	X = []
	for i in range(0, len(x)):
		X.append(minedict[x[i][0]])
	x_train, x_test, y_train, y_test = train_test_split(X, y, test_size = 0.2, random_state = 0)
	
	tree.fit(x_train, y_train)

	rsq_train = tree.score(x_train, y_train)
	rsq_test = tree.score(x_test, y_test)
	w = tree.feature_importances_
	
	error_test = abs(tree.predict(x_test) - y_test)
	mse = np.square(error_test).mean()

	result_full = tree.predict(X)
	plt.plot(qtrsd, result_full)
	plt.show()

	future_close = date(2025, 1, 1)
	future_far = date(2100, 1, 1)
	recent = X[-1]
	future = [[recent[0], recent[1], to_int(future_close)], [2*recent[0], 2*recent[1], to_int(future_far)], [0.5*recent[0], 0.5*recent[1], to_int(future_far)]]
	tree.fit(X, y)
	prediction = tree.predict(future)

	correlations.append([d, rsq_train, rsq_test, w.tolist(), mse, prediction.tolist()])

correlations.sort(reverse = True)
for u in correlations:
	print(u)
