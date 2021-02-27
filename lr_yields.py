#-------------------------------------------------------------------------------
#
# Title:          Plot Effect of LR Treasury Yields on FOMC Announcement Days
#                 Hildebrand (2020)
#
# Author:         Matt Carl
#
# Date:           February 26, 2021
#
# Date Updated:
#
# Input:          macro_financial_announcement_data.xlsx
#
# Output:         10y_treasury.pdf
#
#-------------------------------------------------------------------------------


### Import packages
from functools import reduce
import datetime as dt
import pandas as pd
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
%matplotlib notebook
#%matplotlib inline
import os
import math

path = "/Users/matthewcarl/Dropbox/research/ml_announcements/"
os.chdir(path)
data = pd.read_excel('data/final/macro_financial_announcement_data.xlsx',engine='openpyxl')

def log_growth(series):
    out = []
    for i in range(len(series)):
            if i == 0:
                    out.append(np.nan)
            else:
                    out.append(np.log(series[i]/series[i-1]))
    out = pd.Series(out)
    out.index = series.index
    return out

treasury10y_d = data[['treasury10y_d','FOMC','date_d']]
treasury10y_d = treasury10y_d[treasury10y_d['date_d']>'1984-01-29']
treasury10y_d['FOMC'] = treasury10y_d['FOMC'].fillna(0)
treasury10y_d.index=treasury10y_d['date_d']
treasury10y_d = treasury10y_d.dropna(how='any')
treasury10y_d['treasury10y_pch_d'] = log_growth(treasury10y_d['treasury10y_d'])
treasury10y_d['FOMC_3'] = treasury10y_d['FOMC']+treasury10y_d['FOMC'].shift(1).fillna(0) + treasury10y_d['FOMC'].shift(-1).fillna(0)

treasury10y_d['treasury10y_pch_d_FOMC'] = treasury10y_d['treasury10y_pch_d']
treasury10y_d.loc[treasury10y_d.FOMC_3==0,'treasury10y_pch_d_FOMC'] = 0

treasury10y_d['treasury10y_pch_d_noFOMC'] = treasury10y_d['treasury10y_pch_d']
treasury10y_d.loc[treasury10y_d.FOMC_3==1,'treasury10y_pch_d_noFOMC'] = 0

plot = treasury10y_d[['treasury10y_pch_d','treasury10y_pch_d_FOMC','treasury10y_pch_d_noFOMC']]
plot = np.cumsum(plot)

plt.clf()
fig, ax = plt.subplots()
plot[plot.columns[0]].plot(ax=ax, color='navy', label="10-Year Treasury")
plot[plot.columns[1]].plot(ax=ax, color='maroon', label="10-Year Treasury (FOMC)")
plot[plot.columns[2]].plot(ax=ax, color='orange', label="10-Year Treasury (No FOMC)")
ax.set_xlabel('Date')
ax.set_ylabel('Cumulative Yield Change (%)')
plt.legend()

fig.savefig("output/10y_treasury.pdf",dpi=300)
