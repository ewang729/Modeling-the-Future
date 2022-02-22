import pandas as pd

filename = "Arizona_pH.csv"

minnum = 30  # minimum number of measured values per site
minres, maxres = 2, 12  # filter out extreme outliers

properties = ['ActivityStartDate', 'MonitoringLocationIdentifier', 'ActivityLocation/LatitudeMeasure', 'ActivityLocation/LongitudeMeasure',
'ResultMeasureValue', 'ResultMeasure/MeasureUnitCode']
df = pd.read_csv("raw data/" + filename, usecols = properties)
df.rename(columns = {'ActivityStartDate' : 'date', 'MonitoringLocationIdentifier' : 'loc', 'ActivityLocation/LatitudeMeasure' : 'latitude',
'ActivityLocation/LongitudeMeasure' : 'longitude', 'ResultMeasureValue' : 'res', 'ResultMeasure/MeasureUnitCode' : 'unit'}, inplace = True)
df['res'] = pd.to_numeric(df['res'], errors = 'coerce')
df['date'] = pd.to_datetime(df['date'], errors = 'coerce')
df['res'].fillna(0.0, inplace = True)
df = df.dropna()

num = {}  # number of measurements per location
bad = set()  # set of rows to remove
for line, row in enumerate(df.itertuples(), 1):
	if row.res < minres or row.res > maxres:  # likely error in measurement
		bad.add(row.Index)
	else:
		if row.loc in num:
			num[row.loc] = num[row.loc] + 1
		else:
			num[row.loc] = 1

# remove locations without enough data points
for line, row in enumerate(df.itertuples(), 1):
	if num[row.loc] < minnum:
		bad.add(row.Index)

df.drop(list(bad), inplace = True)

print(df)

df.to_csv("cleaned data expanded/" + filename, index = False)
