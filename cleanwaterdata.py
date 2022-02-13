import pandas as pd
from statistics import mean

filename = "Arizona_pH.csv"
minlocations = 10

properties = ['ActivityStartDate', 'MonitoringLocationIdentifier', 'ActivityLocation/LatitudeMeasure', 'ActivityLocation/LongitudeMeasure',
'ResultMeasureValue', 'ResultMeasure/MeasureUnitCode']
df = pd.read_csv("raw data/" + filename, usecols = properties)
df.rename(columns = {'ActivityStartDate' : 'date', 'MonitoringLocationIdentifier' : 'loc', 'ActivityLocation/LatitudeMeasure' : 'latitude',
'ActivityLocation/LongitudeMeasure' : 'longitude', 'ResultMeasureValue' : 'res', 'ResultMeasure/MeasureUnitCode' : 'unit'}, inplace = True)
df['res'] = pd.to_numeric(df['res'], errors = 'coerce')
df['date'] = pd.to_datetime(df['date'], errors = 'coerce')
df['res'].fillna(0.0, inplace = True)
df = df.dropna()
print(df)
locations = set()
for x in df['loc']:
	locations.add(x)
print(str(len(locations)) + " locations")
condensed = {}
coord = {}
allunits = set()
for line, row in enumerate(df.itertuples(), 1):
	allunits.add(row.unit)
	if row.unit == 'ug/l':
		print(row.Index)
		df.at[row.Index, 'unit'] = 'mg/l'
		df.at[row.Index, 'res'] = row.res / 1000
print(allunits)
for line, row in enumerate(df.itertuples(), 1):
	key = (row.date.year, row.loc)
	if key in condensed:
		condensed[key].append(row.res)
	else:
		condensed[key] = [row.res]
	coord[row.loc] = (row.latitude, -abs(row.longitude))

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
	if(num[key[1]] < minlocations):
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
