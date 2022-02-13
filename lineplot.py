import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

filename = "Arizona_pH.csv"
df = pd.read_csv("cleaned data/" + filename)
#df['date'] = pd.to_datetime(df['date'])
df.sort_values('date', inplace = True)
print(df)
dates = {}
results = {}
coords = {}
for row in df.itertuples():
	if row.res < 3 or row.res > 12:
		continue
	p = row.loc
	if p in dates:
		dates[p].append(row.date)
		results[p].append(row.res)
	else:
		dates[p] = [row.date]
		results[p] = [row.res]
		coords[p] = [row.latitude, row.longitude]

slopes = []

for key in dates:
	x, y = dates[key], results[key]
	plt.plot(x, y)
	m, b = np.polyfit(x, y, 1)
	slopes.append([m, coords[key]])

slopes.sort()
print(slopes)

plt.title("pH levels in Arizona")
plt.xlabel("date")
plt.ylabel("pH")
plt.show()
