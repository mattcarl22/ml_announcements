#-------------------------------------------------------------------------------
#
# Title:          Plot Effect of FOMC Announcement on Log Returns
#
# Author:         Matt Carl
#
# Date:           January 20, 2021
#
# Date Updated:
#
# Input:          macro_financial_announcement_data.xlsx
#
# Output:         ret_fomc.pdf
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


### Setup
# Import data
path = "/Users/matthewcarl/Dropbox/research/ml_announcements/"
os.chdir(path)
data = pd.read_excel('data/final/macro_financial_announcement_data.xlsx',engine='openpyxl')

# Keep relevant variables
data_reg = data[['date_d','FOMC', 'log_r']]

# Add back a few lag days for the first FOMC announcement
data_reg = data_reg[data_reg.date_d>'1984-01-29']
data_reg['FOMC'] = data_reg['FOMC'].fillna(0)
data_reg = data_reg.dropna(how='any')

# Add lags/leads
for l in range(-2,3):
    data_reg['FOMC_l_' + str(l)] = data_reg['FOMC'].shift(l).fillna(0)

del data_reg['FOMC']


### Run linear regression r_t = a + b*FOMC_t + u
# All years
x=data_reg.filter(regex='FOMC')
y=data_reg['log_r']
model_all = sm.OLS(y, sm.add_constant(x)).fit()
coef_all = pd.DataFrame(model_all.params).rename(columns={0:'coef'})
ci_all = model_all.conf_int(alpha=0.05, cols=None).rename(columns={0:'ci_l',1:'ci_u'})
plot_all = pd.concat([coef_all,ci_all],axis=1)

# 1980s
x=data_reg.filter(regex='FOMC')[data_reg.date_d<'1990-01-01']
y=data_reg.loc[data_reg.date_d<'1990-01-01','log_r']
model_1980 = sm.OLS(y, sm.add_constant(x)).fit()
coef_1980 = pd.DataFrame(model_1980.params).rename(columns={0:'coef'})
ci_1980 = model_1980.conf_int(alpha=0.05, cols=None).rename(columns={0:'ci_l',1:'ci_u'})
plot_1980 = pd.concat([coef_1980,ci_1980],axis=1)

# 1990s
x=data_reg.filter(regex='FOMC')[(data_reg.date_d>='1990-01-01') & (data_reg.date_d < '2000-01-01')]
y=data_reg.loc[(data_reg.date_d>='1990-01-01') & (data_reg.date_d < '2000-01-01'), 'log_r']
model_1990 = sm.OLS(y, sm.add_constant(x)).fit()
coef_1990 = pd.DataFrame(model_1990.params).rename(columns={0:'coef'})
ci_1990 = model_1990.conf_int(alpha=0.05, cols=None).rename(columns={0:'ci_l',1:'ci_u'})
plot_1990 = pd.concat([coef_1990,ci_1990],axis=1)

# 2000s
x=data_reg.filter(regex='FOMC')[(data_reg.date_d>='2000-01-01') & (data_reg.date_d < '2010-01-01')]
y=data_reg.loc[(data_reg.date_d>='2000-01-01') & (data_reg.date_d < '2010-01-01'), 'log_r']
model_2000 = sm.OLS(y, sm.add_constant(x)).fit()
coef_2000 = pd.DataFrame(model_2000.params).rename(columns={0:'coef'})
ci_2000 = model_2000.conf_int(alpha=0.05, cols=None).rename(columns={0:'ci_l',1:'ci_u'})
plot_2000 = pd.concat([coef_2000,ci_2000],axis=1)

# 2010s
x=data_reg.filter(regex='FOMC')[(data_reg.date_d>='2010-01-01') & (data_reg.date_d < '2020-01-01')]
y=data_reg.loc[(data_reg.date_d>='2010-01-01') & (data_reg.date_d < '2020-01-01'), 'log_r']
model_2010 = sm.OLS(y, sm.add_constant(x)).fit()
coef_2010 = pd.DataFrame(model_2010.params).rename(columns={0:'coef'})
ci_2000 = model_2010.conf_int(alpha=0.05, cols=None).rename(columns={0:'ci_l',1:'ci_u'})
plot_2010 = pd.concat([coef_2010,ci_2000],axis=1)


### Plot figure
x=range(-2,3)
period=['All','1980s','1990s','2000s','2010s']
plot_list=[plot_all,plot_1980,plot_1990,plot_2000,plot_2010]
plt.clf()
fig = plt.figure(1)
gridspec.GridSpec(3,2)

for i in range(0, 5):
    if i==0:
        plt.subplot2grid((3,2), (0,0), colspan=2)
        plt.axhline(y=0, color='black', linestyle = '-', linewidth=0.75)
        plt.plot(x,plot_list[i]['coef'].values[1:], color='blue')
        plt.plot(x,plot_list[i]['ci_l'].values[1:], color='red', linestyle=':')
        plt.plot(x,plot_list[i]['ci_u'].values[1:], color='red', linestyle=':')
        plt.title(period[i])
        plt.xticks(range(-2,3))
    else:
        if i==1:
            j=1 #row number \in [0,2]
            k=0 #column number \in [0,1]
        if i==2:
            j=1
            k=1
        if i==3:
            j=2
            k=0
        if i==4:x
            j=2
            k=1
        plt.subplot2grid((3,2), (j,k))
        plt.axhline(y=0, color='black', linestyle = '-', linewidth=0.75)
        plt.plot(x,plot_list[i]['coef'].values[1:], color='blue')
        plt.plot(x,plot_list[i]['ci_l'].values[1:], color='red', linestyle=':')
        plt.plot(x,plot_list[i]['ci_u'].values[1:], color='red', linestyle=':')
        plt.title(period[i])
        plt.xticks(range(-2,3))

fig.suptitle("Log Returns on FOMC Announcement Days")
fig.tight_layout()
fig.savefig("output/ret_fomc.pdf",dpi=300)
