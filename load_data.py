#-------------------------------------------------------------------------------
#
# Title:          Load master data into ordered array for analysis
#
# Author:         Matt Carl
#
# Date:           March 11, 2021
#
# Date Updated:   March 25, 2021
#
# Input:          data/final/macro_financial_announcement_data.xlsx,
#                 data/final/varlist.xlsx
#
# Output:         data/final/data_analysis.xlsx
#
#-------------------------------------------------------------------------------

### Import packages
import pandas as pd
import numpy as np
import os

def load_data(user=os.getlogin(), output_excel=1):
    if user=='matthewcarl':
        path = "/Users/matthewcarl/Dropbox/research/ml_announcements/"
    elif user=="": #Sebastian can enter his local username here: print(os.getlogin())
        path = "" #Sebastian can enter his path here

    ### Read data
    os.chdir(path)
    data = pd.read_excel('data/final/macro_financial_announcement_data.xlsx',engine='openpyxl')

    # Keep relevant dates
    data = data[(data['weekend'] == 0) & (data['Date'] >= '1990-01-01') &
                (data['Date'] < '2020-01-01')]
    data = data.set_index(data['Date'])
    del data['Date']

    ### Keep relevant variables for analysis
    vars = pd.read_excel('data/final/varlist.xlsx',engine='openpyxl')

    # The first column is the announcement variable; all subsequent columns are the features
    var_list = [vars['Announcement Indicator'][0]]+
                list(vars['Main variables to include'].dropna())
    data = data[var_list]

    ### Fix missing data
    # USD-EUR exchange rate
    data['exchg_useur_d']=data['exchg_useur_d'].fillna(0)

    # Fill other missing data with previous observation (for now) and drop other missing rows
    data = data.ffill()
    data = data.dropna()

    if output_excel==1:
        data.to_excel('data/final/data_analysis.xlsx', index=True,
                      index_label='Date', na_rep='NULL')
    else:
        return data

### Example function call
# 2 Arguments:
#   1. user=os.getlogin() - don't need to change this (will read from your local machine)
#   2. output_excel=1  - if you want to export the final data to an excel file
#                  =0  - if you want to return the data to memory
load_data(user=os.getlogin(), output_excel=1)
#data=load_data(user=os.getlogin(), output_excel=0)
