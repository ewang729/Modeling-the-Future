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
for row in df.itertuples():
	if row.res > 10 or row.res < 5:
		continue
	if row.loc in dates:
		dates[row.loc].append(row.date)
		results[row.loc].append(row.res)
	else:
		dates[row.loc] = [row.date]
		results[row.loc] = [row.res]

for key in dates:
    x, y = dates[key], results[key]
    plt.plot(x, y)
    m, b = np.polyfit(x, y, 1)
    print(m)

plt.title("pH in Arizona")
plt.xlabel("date")
plt.ylabel("pH")
plt.show()
