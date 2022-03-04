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
from lineartree import LinearBoostRegressor as lbr
from statistics import mean
from math import sqrt

mine_name = "Morenci"
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
	minedict[key] = [row.mining + row.plant, key]

# function to generate list of production quarters in range of years
md = [[3, 31], [6, 30], [9, 30], [12, 31]]
def quarters(start, end):
	qtrs = []
	for i in range(start, end + 1):
		for j in range(0, 4):
			dt = date(i, md[j][0], md[j][1])
			if to_int(dt) in minedict:
				qtrs.append([to_int(dt), dt])
	return qtrs

# create Linear Forest Regression model
tree = lfr(base_estimator = lr(), min_samples_split = 8)

correlations = []

# run model
for d in locations:
	current = water[water['distance'] == d]

	if d > 30:  # only use locations within 30 km of the mine
		continue

	pH = []

	for row in current.itertuples():
		pH.append([to_int(row.date), row.date, row.res])
	
	# generate list of production quarters in range of measurements
	pH.sort()
	start_year = pH[0][1].year
	end_year = pH[-1][1].year
	qtrs = np.array(quarters(start_year, end_year))
	qtrs_int = qtrs[:,0]
	qtrs_date = qtrs[:,1]
	
	# skip locations without enough data
	if len(qtrs) < 10 or len(pH) < 10:
		continue

	# format dataset for KNN
	x = []
	y = []
	dates = []
	
	for i in range(0, len(pH)):
		x.append(pH[i][0])
		y.append(pH[i][2])
		dates.append(pH[i][1])
	
	plt.scatter(dates, y)
	x = np.array(x).reshape(-1, 1)
	qtrs_int = np.array(qtrs_int).reshape(-1, 1)

	# interpolate water pH with KNN
	knn = neighbors.KNeighborsRegressor(7, weights = 'uniform')
	inter = knn.fit(x, y).predict(qtrs_int)
	
	x = qtrs
	y = inter
	plt.scatter(qtrs_date, y)
	
	# collect mining data per production quarter
	X = []
	for i in range(0, len(x)):
		X.append(minedict[x[i][0]])
	
	# split data for training and testing
	x_train, x_test, y_train, y_test = train_test_split(X, y, test_size = 0.2, random_state = 0)
	
	# fit model
	tree.fit(x_train, y_train)

	# calculate error and feature importance
	rsq_train = tree.score(x_train, y_train)
	rsq_test = tree.score(x_test, y_test)
	w = tree.feature_importances_

	error_test = abs(tree.predict(x_test) - y_test)
	mse = np.square(error_test).mean()
	
	# plot results
	result_full = tree.predict(X)
	plt.plot(qtrs_date, result_full)
	plt.title('pH against date')
	plt.xlabel('date')
	plt.ylabel('water pH')
	plt.show()

	future_close = date(2025, 1, 1)
	future_far = date(2100, 1, 1)
	recent = X[-1]
	future = [[recent[0] + recent[1], to_int(future_close)], [2*recent[0] + 2*recent[1], to_int(future_far)], [0, to_int(future_far)]]
	tree.fit(X, y)
	prediction = tree.predict(future)

	correlations.append([d, rsq_train, rsq_test, w.tolist(), mse, prediction.tolist()])

correlations.sort(reverse = True)
for u in correlations:
	print(u)
