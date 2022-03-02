import pandas as pd

filename = "Morenci_Mine.csv"

properties = ['Prod Qtr.', 'Type', 'Quarterly Hrs.']
df = pd.read_csv("raw data/" + filename, usecols = properties, thousands = ',')
df.rename(columns = {'Prod Qtr.' : 'date', 'Mine Id' : 'id' , 'Type' : 'type', 'Quarterly Hrs.' : 'hrs'}, inplace = True)
pd.to_numeric(df['hrs'])

# function to convert production quarter code into date
def convert(x):
	y = x // 10
	qtr = x % 10
	m, d = 0, 0
	if qtr == 1:
		m, d = 3, 31
	elif qtr == 2:
		m, d = 6, 30
	elif qtr == 3:
		m, d = 9, 30
	else:
		m, d = 12, 31
	return str(m) + "/" + str(d) + "/" + str(y)

# convert production quarter codes
for line, row in enumerate(df.itertuples(), 1):
	df.at[row.Index, 'date'] = convert(row.date)

# create new dataframe with different hour types merged
dates = []
mining = []
plant = []
office = []

for line, row in enumerate(df.itertuples(), 1):
	t = row.type
	if t == "STRIP, QUARY, OPEN PIT":
		dates.append(row.date)
		mining.append(row.hrs)
	elif t == "MILL OPERATION/PREPARATION PLANT":
		plant.append(row.hrs)
	elif t == "OFFICE WORKERS AT MINE SITE":
		office.append(row.hrs)

w = min(len(dates), len(mining), len(plant), len(office))
dates = dates[0 : w]  # certain qualities are not tracked for older dates
mining = mining[0 : w]
plant = plant[0 : w]
office = office[0 : w]

d = {'date' : dates, 'mining' : mining, 'plant' : plant, 'office' : office}
df2 = pd.DataFrame(data = d)

print(df2)

df2.to_csv("cleaned data/" + filename, index = False)
