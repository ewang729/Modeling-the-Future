import pandas as pd

filename = "Bagdad_Mine.csv"

properties = ['Prod Qtr.', 'Mine ID', 'Subunit', 'Quarterly Hrs.']
df = pd.read_csv("raw data/" + filename, usecols = properties, thousands = ',')
df.rename(columns = {'Prod Qtr.' : 'date', 'Mine Id' : 'id' , 'Subunit' : 'type', 'Quarterly Hrs.' : 'hrs'}, inplace = True)
pd.to_numeric(df['hrs'])

# convert production quarter code into date
for line, row in enumerate(df.itertuples(), 1):
	x = row.date
	year = x // 10
	qtr = x % 10
	md = ""
	if qtr == 1:
		md = "3/31/" 
	elif qtr == 2:
		md = "6/30/"
	elif qtr == 3:
		md = "9/30/"
	else:
		md = "12/31/"
	df.at[row.Index, 'date'] = md + str(year)

print(df)

df.to_csv("cleaned data/" + filename, index = False)
