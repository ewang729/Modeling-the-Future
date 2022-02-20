import pandas as pd

filename = "Arizona_pH.csv"
minlocations = 30
minres = 2
maxres = 12

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
num = {}
bad = set()
for line, row in enumerate(df.itertuples(), 1):
	if row.res < minres or row.res > maxres:
		bad.add(row.Index)
	else:
		if row.loc in num:
			num[row.loc] = num[row.loc] + 1
		else:
			num[row.loc] = 1
for line, row in enumerate(df.itertuples(), 1):
	if num[row.loc] < minlocations:
		bad.add(row.Index)
print(len(bad))
df.drop(list(bad), inplace = True)
df.to_csv("cleaned data expanded/" + filename, index = False)
