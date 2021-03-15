#-------------------------------------------------------------------------------
#
# Title:          Load master data into ordered array for analysis
#
# Author:         Matt Carl
#
# Date:           March 11, 2021
#
# Date Updated:
#
# Input:          macro_financial_announcement_data.xlsx, varlist.xlsx
#
# Output:
#
#-------------------------------------------------------------------------------

### Import packages
import pandas as pd
import numpy as np
import os

### Read data
path = "/Users/matthewcarl/Dropbox/research/ml_announcements/"
os.chdir(path)

data = pd.read_excel('data/final/macro_financial_announcement_data.xlsx',engine='openpyxl')

# Keep relevant dates
data = data[(data['weekend'] == 0) & (data['Date'] >= '1990-01-01') & (data['Date'] < '2020-01-01')]
data = data.reset_index(drop=True)

### Keep relevant variables for analysis
vars = pd.read_excel('data/final/varlist.xlsx',engine='openpyxl')

# The first column is the announcement variable; all subsequent columns are the features
var_list = [vars['Announcement Indicator'][0]]+list(vars['Main variables to include'].dropna())
data = data[var_list]

### Fix missing data
# USD-EUR exchange rate
data['exchg_useur_d']=data['exchg_useur_d'].fillna(0)

# Fill other missing data with previous observation (for now) and drop other missing rows
data = data.ffill()
data = data.dropna()
