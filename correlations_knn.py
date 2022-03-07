import pandas as pd
from haversine import haversine
from datetime import date
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as dates
import numpy as np
from sklearn.tree import DecisionTreeRegressor as dtr
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor as rfr
from sklearn import neighbors
from sklearn.linear_model import LinearRegression as lr
from sklearn import linear_model
from lineartree import LinearTreeRegressor as ltr
from lineartree import LinearForestRegressor as lfr
from lineartree import LinearBoostRegressor as lbr
from statistics import mean
from math import sqrt

mine_name = "Morenci"
mine_file = mine_name + "_Mine.csv"
water_file = "Arizona_pH.csv"

coords_key = {"Morenci" : (33.0635, -109.3353), "Bagdad" : (34.5847, -113.2111), "Ray" : (33.1301, -110.9790), "Safford" : (32.9462, -109.6496)}
coords = coords_key[mine_name]

mine = pd.read_csv("cleaned data/" + mine_file)
water = pd.read_csv("cleaned data expanded/" + water_file)
water['date'] = pd.to_datetime(water['date'])
mine['date'] = pd.to_datetime(mine['date'])

print(mine)
print(water)

# function to convert date to integer
def dt_to_int(dt):
	return 365*dt.year + 30*(dt.month - 1) + dt.day

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
	key = dt_to_int(row.date)
	minedict[key] = [row.mining + row.plant, key]

# function to generate list of production quarters in range of years
md = [[3, 31], [6, 30], [9, 30], [12, 31]]
def quarters(start, end, safe):
	qtrs = []
	for i in range(start, end + 1):
		for j in range(0, 4):
			dt = date(i, md[j][0], md[j][1])
			if (dt_to_int(dt) in minedict) or (not safe):
				qtrs.append([dt_to_int(dt), dt])
	return np.array(qtrs)

# create Linear Forest Regression model
lin_reg = linear_model.LinearRegression()
tree = lbr(base_estimator = lin_reg, loss = "square", min_samples_split = 2, n_estimators = 5)

correlations = []

# run model
for d in locations:
	current = water[water['distance'] == d]

	if d > 75:  # only use locations within 75 km of the mine
		continue
	
	pH = []
	
	lat_long = []
	for row in current.itertuples():
		pH.append([dt_to_int(row.date), row.date, row.res])
		lat_long = [row.latitude, row.longitude]
	
	# generate list of production quarters in range of measurements
	pH.sort()
	start_year = pH[0][1].year
	end_year = pH[-1][1].year
	qtrs = quarters(start_year, end_year, True)

	# skip locations without enough data
	if len(qtrs) < 20 or len(pH) < 20:
		continue

	qtrs_int = qtrs[:,0]
	qtrs_date = qtrs[:,1]

	# skip locations without recent data
	if end_year < 2005:
		continue

	# format dataset for KNN
	x = []
	y = []
	dates = []
	
	for i in range(0, len(pH)):
		x.append(pH[i][0])
		y.append(pH[i][2])
		dates.append(pH[i][1])
	
	fig, ax1 = plt.subplots()
	ax1.scatter(dates, y, label = 'raw pH', color = 'royalblue')
	x = np.array(x).reshape(-1, 1)
	qtrs_int = np.array(qtrs_int).reshape(-1, 1)

	# interpolate water pH with KNN
	knn = neighbors.KNeighborsRegressor(7, weights = 'uniform')
	inter = knn.fit(x, y).predict(qtrs_int)
	
	x = qtrs
	y = inter
	ax1.scatter(qtrs_date, y, label = 'estimated pH (KNN)', color = 'navy')
	
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
	w = tree.coef_
	w = np.array([])
	
	# skip locations with low correlation
	if rsq_test < 0.2:
		plt.close('all')
		continue

	error_test = abs(tree.predict(x_test) - y_test)
	mse = np.square(error_test).mean()
	
	# model future mine activity values
	reg = lr()
	
	mine_x = []
	mine_y = []
	for key in minedict:
		mine_x.append([key])
		mine_y.append(minedict[key][0])

	reg.fit(mine_x, mine_y)
	future = quarters(end_year, 2060, False)
	future_int = future[:,0]
	future_date = future[:,1]
	future_int = future_int.reshape(-1, 1)
	future_mine = reg.predict(future_int)
	new_minedict = {}
	latest = 0
	for i in range(0, len(future_int)):
		key = future_int[i][0]
		if key not in minedict:
			new_minedict[key]= future_mine[i]
		else:
			latest = key

	# predict future water pH levels
	future_x = []
	constant_x = []
	zero_x = []
	for i in range(0, len(future_mine)):
		key = future_int[i][0]
		if key in minedict:
			future_x.append([minedict[key][0], key])
			constant_x.append([minedict[key][0], key])
			zero_x.append([minedict[key][0], key])
		else:
			future_x.append([new_minedict[key], key])
			constant_x.append([minedict[latest][0], key])
			zero_x.append([0, key])
	tree.fit(X, y)
	future_water = tree.predict(future_x)
	future_constant = tree.predict(constant_x)
	future_zero = tree.predict(zero_x)
	
	# collect aggregated mine values
	all_years = quarters(start_year, 2060, False)
	all_mine_date = all_years[:,1]
	all_mine_y = []
	for dt in all_mine_date:
		key = dt_to_int(dt)
		if key in minedict:
			all_mine_y.append(minedict[key][0])
		else:
			all_mine_y.append(new_minedict[key])

	# plot results
	result_full = tree.predict(X)
	plt.plot(qtrs_date, result_full, label = "interpolated pH (LBT)", color = "blueviolet")
	ax1.scatter(future_date, future_water, label = "projected future pH", color = 'darkgreen')
	ax1.scatter(future_date, future_constant, label = "pH if mine production doesn't change", color = 'chartreuse')
	ax1.scatter(future_date, future_zero, label = "pH if mine production stops", color = 'lime')
	ax2 = ax1.twinx()
	ax2.scatter(all_mine_date, all_mine_y, color = 'brown', label = "mine activity")
	plt.title('pH against date at ' + str(lat_long))
	ax1.set_xlabel('date')
	ax1.set_ylabel('water pH')
	ax2.set_ylabel('mine activity (hours)')
	#ax1.legend()
	#ax2.legend()
	fig.legend()
	plt.show()
	plt.close('all')

	# add results to array
	correlations.append([d, rsq_train, rsq_test, w.tolist(), mse, future_water[-1], future_constant[-1], future_zero[-1]])

correlations.sort(reverse = True)
for u in correlations:
	print(u)
