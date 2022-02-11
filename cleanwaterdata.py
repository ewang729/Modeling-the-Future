import pandas as pd
from statistics import mean

filename = "Arizona_pH.csv"
properties = ['ActivityStartDate', 'MonitoringLocationIdentifier', 'ActivityLocation/LatitudeMeasure', 'ActivityLocation/LongitudeMeasure', 'ResultMeasureValue']
df = pd.read_csv("raw data/" + filename, usecols = properties)
df.rename(columns = {'ActivityStartDate' : 'date', 'MonitoringLocationIdentifier' : 'loc', 'ActivityLocation/LatitudeMeasure' : 'latitude', 'ActivityLocation/LongitudeMeasure' : 'longitude', 'ResultMeasureValue' : 'res'}, inplace = True)
df['res'] = pd.to_numeric(df['res'], errors = 'coerce')
df['date'] = pd.to_datetime(df['date'], errors = 'coerce')
df = df.dropna()
print(df)
locations = set()
for x in df['loc']:
	locations.add(x)
print(str(len(locations)) + " locations")
condensed = {}
coord = {}
for row in df.itertuples():
	key = (row.date.year, row.loc)
	if key in condensed:
		condensed[key].append(row.res)
	else:
		condensed[key] = [row.res]
	coord[row.loc] = (row.latitude, row.longitude)

num = {}
for key in condensed:
	if key[1] in num:
		num[key[1]] = num[key[1]] + 1
	else:
		num[key[1]] = 1
dates = []
locs = []
lats = []
longs = []
results = []
for key in condensed:
	if(num[key[1]] < 10):
		continue
	dates.append(key[0])
	locs.append(key[1])
	lats.append(coord[key[1]][0])
	longs.append(coord[key[1]][1])
	results.append(mean(condensed[key]))
data = {'date' : dates, 'loc' : locs, 'latitude' : lats, 'longitude' : longs, 'res' : results}
df2 = pd.DataFrame(data)
df2.sort_values(by = ['loc'])
print(df2)
df2.to_csv("cleaned data/" + filename, index = False)
