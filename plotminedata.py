import matplotlib.pyplot as plt
import matplotlib.dates
import numpy as np
import pandas as pd

filename = "Morenci_Mine.csv"

df = pd.read_csv("cleaned data/" + filename)
df = df[df['type'] == "Total"]
print(df)
df['date'] = pd.to_datetime(df['date'])
plt.plot(df['date'], df['hrs'])
plt.show()
