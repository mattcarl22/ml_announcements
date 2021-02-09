#-------------------------------------------------------------------------------
#
# Title:          Assemble Data
#
# Author:         Matt Carl
#
# Date:           December 8, 2020
#
# Date Updated:   February 4, 2021
#
# Input:          FRED (API), fomc_dates.csv, gdp_announcement_dates.csv,
#                 bls_announcement_dates.xlsx, manual FRED download (various),
#                 Fama-French returns (various), CRSP returns (pd_ratio.xls)
#
# Output:         macro_financial_announcement_data.xlsx
#
#-------------------------------------------------------------------------------

### Setup
from fredapi import Fred
fred = Fred(api_key='2f4b2a2f6b2401149c51f89021f47f49')

from functools import reduce
import datetime as dt
import pandas as pd
import numpy as np
import datetime as dt
import os
path_in = "/Users/matthewcarl/Dropbox/research/ml_announcements/data/raw"
path_out = "/Users/matthewcarl/Dropbox/research/ml_announcements/data/final"

#-------------------------------------------------------------------------------
### Pull FRED Series
ffr_d             = fred.get_series('DFF', observation_start='1954-07-01')
ted_d             = fred.get_series('TEDRATE', observation_start='1986-01-02')
treasury30y_d     = fred.get_series('DGS30', observation_start='1977-02-15')
treasury10y_d     = fred.get_series('DGS10', observation_start='1962-01-02')
treasury10ym2y_d  = fred.get_series('T10Y2Y', observation_start='1976-06-01')
treasury5y_d      = fred.get_series('DGS5', observation_start='1962-01-02')
treasury2y_d      = fred.get_series('DGS2', observation_start='1976-06-01')
treasury1y_d      = fred.get_series('DGS1', observation_start='1962-01-02')
treasury6m_d      = fred.get_series('DGS6MO', observation_start='1981-09-01')
treasury3m_d      = fred.get_series('DGS3MO', observation_start='1981-09-01')
exchg_usuk_d      = fred.get_series('DEXUSUK', observation_start='1971-01-04')
exchg_useur_d     = fred.get_series('DEXUSEU', observation_start='1999-01-04')
exchg_suius_d     = fred.get_series('DEXSZUS', observation_start='1971-01-04')
exchg_canus_d     = fred.get_series('DEXCAUS', observation_start='1971-01-04')
exchg_usaus_d     = fred.get_series('DEXUSAL', observation_start='1971-01-04')
exchg_chius_d     = fred.get_series('DEXCHUS', observation_start='1981-01-02')
exchg_jpus_d      = fred.get_series('DEXJPUS', observation_start='1971-01-04')
exchg_skus_d      = fred.get_series('DEXKOUS', observation_start='1981-04-13')
exchg_indus_d     = fred.get_series('DEXINUS', observation_start='1973-01-02')
recessions_d      = fred.get_series('USRECD', observation_start='1920-02-01')
epu_d             = fred.get_series('USEPUINDXD', observation_start='1985-01-01')
ur_w              = fred.get_series('IURSA', observation_start='1971-01-02')
ur_m              = fred.get_series('UNRATE', observation_start='1948-01-01')
emp_m             = fred.get_series('PAYEMS', observation_start='1939-01-01')
cons_m            = fred.get_series('PCE', observation_start='1959-01-01')
ind_prod_m        = fred.get_series('INDPRO', observation_start='1920-02-01')
um_csent_m        = fred.get_series('UMCSENT', observation_start='1952-11-01')
cpi_m             = fred.get_series('CPIAUCSL', observation_start='1947-01-01')
mort_rate30y_w    = fred.get_series('MORTGAGE30US', observation_start='1971-04-02')
cbyield_aaa_d     = fred.get_series('DAAA', observation_start='1983-01-03')
cbyield_baa_d     = fred.get_series('DBAA', observation_start='1986-01-02')
cbyield_aaa_w     = fred.get_series('WAAA', observation_start='1962-01-05')
cbyield_baa_w     = fred.get_series('WBAA', observation_start='1962-01-05')
oil_d             = fred.get_series('DCOILWTICO', observation_start='1986-01-02')
nikkei_d          = fred.get_series('NIKKEI225', observation_start='1949-05-16')
nfci_w            = fred.get_series('NFCI', observation_start='1971-01-08')
m2_w              = fred.get_series('M2', observation_start='1980-11-10')
gov_dep_w         = fred.get_series('GDTCBW', observation_start='1975-01-06')
bk_prime_rate_w   = fred.get_series('WPRIME', observation_start='1955-05-10')
bk_dep_w          = fred.get_series('DPSACBW027SBOG', observation_start='1973-01-03')
bk_liab_w         = fred.get_series('TLBACBW027NBOG', observation_start='1973-01-03')
bk_asset_w        = fred.get_series('TLAACBW027SBOG', observation_start='1973-01-03')
bk_cred_w         = fred.get_series('TOTBKCR', observation_start='1973-01-03')
bk_cash_w         = fred.get_series('CASACBW027SBOG', observation_start='1973-01-03')

#-------------------------------------------------------------------------------
# Calculate log growth of non-stationary series
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

emp_pch_m = log_growth(emp_m)
cons_pch_m = log_growth(cons_m)
ind_prod_pch_m = log_growth(ind_prod_m)
inflation_m = log_growth(cpi_m)
nikkei_ret_d = log_growth(nikkei_d)
m2_pch_w = log_growth(m2_w)
bk_dep_pch_w = log_growth(bk_dep_w)
bk_liab_pch_w = log_growth(bk_liab_w)
bk_asset_pch_w = log_growth(bk_asset_w)
bk_cred_pch_w = log_growth(bk_cred_w)
bk_cash_pch_w = log_growth(bk_cash_w)

# Data not available in FRED API (pulled manually, see below)
# libor12m_d      = fred.get_series('USD12MD156N', observation_start='1986-01-02')
# libor6m_d       = fred.get_series('USD6MTD156N', observation_start='1986-01-02')
# libor3m_d       = fred.get_series('USD3MTD156N', observation_start='1986-01-02')
# libor1m_d       = fred.get_series('USD1MTD156N', observation_start='1986-01-02')
# gold_d          = fred.get_series('GOLDAMGBD228NLBM', observation_start='1968-04-01')

### Merge Data
df_d = [ffr_d, ted_d, treasury30y_d, treasury10y_d, treasury10ym2y_d,
        treasury5y_d, treasury2y_d, treasury1y_d, treasury6m_d, treasury3m_d,
        exchg_usuk_d, exchg_useur_d, exchg_suius_d, exchg_canus_d,
        exchg_usaus_d, exchg_chius_d, exchg_jpus_d, exchg_skus_d, exchg_indus_d,
        recessions_d, epu_d, cbyield_aaa_d, cbyield_baa_d, oil_d, nikkei_ret_d]
sname_d = ['ffr_d', 'ted_d', 'treasury30y_d', 'treasury10y_d', 'treasury10ym2y_d',
           'treasury5y_d', 'treasury2y_d', 'treasury1y_d', 'treasury6m_d', 'treasury3m_d',
           'exchg_usuk_d', 'exchg_useur_d', 'exchg_suius_d', 'exchg_canus_d',
           'exchg_usaus_d', 'exchg_chius_d', 'exchg_jpus_d', 'exchg_skus_d', 'exchg_indus_d',
           'recessions_d', 'epu_d', 'cbyield_aaa_d', 'cbyield_baa_d', 'oil_d', 'nikkei_ret_d']

df_w = [ur_w, cbyield_aaa_w, cbyield_baa_w, mort_rate30y_w, nfci_w, m2_pch_w,
        gov_dep_w, bk_prime_rate_w, bk_dep_pch_w, bk_liab_pch_w,
        bk_asset_pch_w, bk_cred_pch_w, bk_cash_pch_w]
sname_w = ['ur_w', 'cbyield_aaa_w', 'cbyield_baa_w', 'mort_rate30y_w', 'nfci_w', 'm2_pch_w',
           'gov_dep_w', 'bk_prime_rate_w', 'bk_dep_pch_w', 'bk_liab_pch_w',
           'bk_asset_pch_w', 'bk_cred_pch_w', 'bk_cash_pch_w']

df_m = [emp_pch_m, cons_pch_m, ind_prod_pch_m, um_csent_m, inflation_m, ur_m]
sname_m = ['emp_pch_m', 'cons_pch_m', 'ind_prod_pch_m', 'um_csent_m', 'inflation_m', 'ur_m']

#-------------------------------------------------------------------------------
for i in range(len(df_d)):
        df_d[i] = df_d[i].rename_axis("Date")
        df_d[i] = df_d[i].rename(sname_d[i])
for i in range(len(df_w)):
        df_w[i] = df_w[i].rename_axis("Date")
        df_w[i].index = df_w[i].index.to_period("W")
        df_w[i] = df_w[i].rename(sname_w[i])
for i in range(len(df_m)):
        df_m[i] = df_m[i].rename_axis("Date")
        df_m[i].index = df_m[i].index.to_period("M")
        df_m[i] = df_m[i].rename(sname_m[i])

data_d = reduce(lambda  l,r: pd.merge(l,r, on='Date', how='outer'), df_d).fillna(np.nan)
data_d.sort_values(by='Date', inplace=True)
data_d["date_d"] = data_d.index.to_period('D')
data_d["date_w"] = data_d.index.to_period('W')
data_d["date_m"] = data_d.index.to_period('M')

data_w = reduce(lambda l,r: pd.merge(l,r,left_index=True, right_index=True, how='outer'), df_w).fillna(np.nan)
data_w.sort_values(by='Date', inplace=True)
data_w_lead=data_w.shift(1)
#data_w
#data_w_lead

data_m = reduce(lambda l,r: pd.merge(l,r,left_index=True, right_index=True, how='outer'), df_m).fillna(np.nan)
data_m.sort_values(by='Date', inplace=True)
data_m_lead=data_m.shift(1)
#data_m
#data_m_lead

# Merge (1-period-lead) weekly and monthly data with daily data
# E.g., week 1 unemployment rate only observed in week 2 daily data, so push
#       weekly and monthly data forward by one period
data = pd.merge(data_d, data_w_lead, left_on="date_w", right_index=True, how='outer').fillna(np.nan)
data = pd.merge(data, data_m_lead, left_on="date_m", right_index=True, how='outer').fillna(np.nan)

# Supplement weekly unemployment rate with monthly historical data
fvi_ur = data.ur_w.first_valid_index()
data['ur_w_m']=data['ur_w']
data.loc[data.index<fvi_ur, 'ur_w_m'] = data['ur_m']

# Supplement daily corporate bond yields with weekly historical data
fvi_cbyield_aaa = data.cbyield_aaa_d.first_valid_index()
data['cbyield_aaa_d_w'] = data['cbyield_aaa_d']
data.loc[data.index<fvi_cbyield_aaa, 'cbyield_aaa_d_w'] = data['cbyield_aaa_w']

fvi_cbyield_baa = data.cbyield_baa_d.first_valid_index()
data['cbyield_baa_d_w'] = data['cbyield_baa_d']
data.loc[data.index<fvi_cbyield_aaa, 'cbyield_baa_d_w'] = data['cbyield_baa_w']

#-------------------------------------------------------------------------------
### FOMC Announcement Data
os.chdir(path_out)
fomc = pd.read_csv('fomc_dates.csv')
fomc.index = pd.to_datetime(fomc['Date'])
del fomc['Date']

# Merge with master data
data_fomc = pd.merge(data, fomc, right_index=True, left_index=True , indicator=True, how="outer")

data_fomc.loc[data_fomc.index < min(fomc.index), 'FOMC'] = np.nan
data_fomc.loc[(data_fomc.index >= min(fomc.index)) & (data_fomc['_merge']=="left_only"), 'FOMC'] = 0
#data_fomc.loc[(data_fomc.index >= min(fomc.index)) & (data_fomc['_merge']=="both"), 'FOMC'] = 1

del data_fomc['_merge']
#data_fomc

#-------------------------------------------------------------------------------
### GDP Announcement Data
os.chdir(path_out)
gdp_ann = pd.read_csv('gdp_announcement_dates.csv')
gdp_ann.index = pd.to_datetime(gdp_ann['date'])
del gdp_ann['date']

gdp_ann.columns = ['GDP_Announcement']
#gdp_ann

# Merge with master data
data_fomc_gdp = pd.merge(data_fomc, gdp_ann, right_index=True, left_index=True , indicator=True, how="outer")
#data_fomc_gdp.tail(50)
data_fomc_gdp['gdp_ann_ind']=np.nan
data_fomc_gdp.loc[(data_fomc_gdp.index >= min(gdp_ann.index)) & (data_fomc_gdp['_merge']=="left_only"), 'gdp_ann_ind'] = 0
data_fomc_gdp.loc[(data_fomc_gdp.index >= min(gdp_ann.index)) & (data_fomc_gdp['_merge']=="both"),'gdp_ann_ind'] = 1
#np.sum(data_fomc_gdp['gdp_ann_ind'])
del data_fomc_gdp['_merge']

#data_fomc_gdp

#-------------------------------------------------------------------------------
### BLS Announcement Data
os.chdir(path_out)
bls_ann = pd.read_excel('bls_announcement_dates.xlsx', engine='openpyxl')
bls_ann.index = pd.to_datetime(bls_ann['date'])
del bls_ann['date']

# Merge with master data
data_fomc_gdp_bls = pd.merge(data_fomc_gdp, bls_ann, right_index=True, left_index=True, how="outer")

bls_ann_ind=['emp_ann','cpi_ann','ppi_ann','eci_ann','mxpi_ann','real_earnings_ann','metro_emp_ann','state_emp_ann','prod_costs_ann']
for i in range(len(bls_ann_ind)):
   i=bls_ann_ind[i]
   fvi=data_fomc_gdp_bls[i].first_valid_index()
   data_fomc_gdp_bls.loc[(data_fomc_gdp_bls.index >= fvi) & (pd.isna(data_fomc_gdp_bls[i])), i] = 0

#data_fomc_gdp_bls

#-------------------------------------------------------------------------------
### Manual FRED data
os.chdir(path_in)
gold_d          = pd.read_excel(r'GOLDAMGBD228NLBM.xls',skiprows=10)
libor12m_d      = pd.read_excel(r'USD12MD156N.xls',skiprows=10)
libor6m_d       = pd.read_excel(r'USD6MTD156N.xls',skiprows=10)
libor3m_d       = pd.read_excel(r'USD3MTD156N.xls',skiprows=10)
libor1m_d       = pd.read_excel(r'USD1MTD156N.xls',skiprows=10)

df_man = [gold_d, libor12m_d, libor6m_d, libor3m_d, libor1m_d]
sname_man = ['gold_d', 'libor12m_d', 'libor6m_d', 'libor3m_d', 'libor1m_d']

for i in range(len(df_man)):
        df_man[i].rename(columns={ df_man[i].columns[0]: "Date",
                                   df_man[i].columns[1] : sname_man[i]
                                 }, inplace=True)
        df_man[i].index = pd.to_datetime(df_man[i]['Date'])
        del df_man[i]['Date']

data_man = reduce(lambda l,r: pd.merge(l, r, right_index=True, left_index=True, how='outer'), df_man).fillna(np.nan)

# Merge with master data
data_fomc_gdp_bls_man = pd.merge(data_fomc_gdp_bls, data_man, right_index=True, left_index=True, how='left')

#-------------------------------------------------------------------------------
### Returns data from CRSP
os.chdir(path_in)
ret       = pd.read_excel(r'pd_ratio.xls')
ret.index = pd.to_datetime(ret['Date'],format='%Y%m%d')
del ret['Date']
#ret

# Merge with master data
data_fomc_gdp_bls_man_ret = pd.merge(data_fomc_gdp_bls_man, ret, right_index=True, left_index=True, how='outer').fillna(np.nan)

#-------------------------------------------------------------------------------
### Returns data from Fama-French
os.chdir(path_in)
# 10-industry portfolios
ff_10ind = pd.read_csv(r'10_Industry_Portfolios_Daily.CSV', skiprows=9)
# Grab index where value weighted returns end
end = np.where(ff_10ind.iloc[:,0]=='  Average Equal Weighted Returns -- Daily')[0][0]
ff_10ind = ff_10ind[ff_10ind.index < end]
#ff_10ind

# Momentum factor
ff_mom = pd.read_csv(r'F-F_Momentum_Factor_daily.CSV', skiprows=13)
ff_mom = ff_mom[:-1]
#ff_mom

# 5-factor returns
ff_5f = pd.read_csv(r'F-F_Research_Data_5_Factors_2x3_daily.CSV', skiprows=3)
#ff_5f

# Operating Profitability
ff_op = pd.read_csv(r'Portfolios_Formed_on_OP_Daily.csv', skiprows=22)
end = np.where(ff_op.iloc[:,0]=='  Equal Weight Returns -- Daily')[0][0]
ff_op = ff_op[ff_op.index < end]
#ff_op

df_ff = [ff_10ind, ff_mom, ff_5f, ff_op]

for i in range(len(df_ff)):
        df_ff[i].rename(columns={ df_ff[i].columns[0]: "Date" }, inplace=True)
        df_ff[i].index = pd.to_datetime(df_ff[i]['Date'], format='%Y%m%d')
        del df_ff[i]['Date']

data_ff = reduce(lambda l,r: pd.merge(l, r, right_index=True, left_index=True, how='outer'), df_ff).fillna(np.nan)
#data_ff

# Merge with master data
data_fomc_gdp_bls_man_ret_ff = pd.merge(data_fomc_gdp_bls_man_ret, data_ff, right_index=True, left_index=True, how='outer').fillna(np.nan)
#data_fomc_gdp_bls_man_ret_ff

#-------------------------------------------------------------------------------
### Finalize data

# Create weekend indicator variable
s = data_fomc_gdp_bls_man_ret_ff.index.to_series()
dow = s.dt.dayofweek
dow = dow.rename("dow")
data_fomc_gdp_bls_man_ret_ff = pd.merge(data_fomc_gdp_bls_man_ret_ff, dow, right_index=True, left_index=True, how='outer').fillna(np.nan)
data_fomc_gdp_bls_man_ret_ff['weekend'] = [0 if x < 5 else 1 for x in data_fomc_gdp_bls_man_ret_ff['dow']]

# Cut tail of data
today=dt.datetime.today().strftime("%Y-%m-%d")
data_fomc_gdp_bls_man_ret_ff = data_fomc_gdp_bls_man_ret_ff[data_fomc_gdp_bls_man_ret_ff.index < today]
#data_fomc_gdp_bls_man_ret_ff

# Drop unneeded variables
#del data_fomc_gdp_bls_man_ret_ff['']


#-------------------------------------------------------------------------------
### Output Final Data
os.chdir(path_out)
data_fomc_gdp_bls_man_ret_ff.shape
data_fomc_gdp_bls_man_ret_ff.to_excel('macro_financial_announcement_data.xlsx', index=True, index_label='Date', na_rep='NULL')
