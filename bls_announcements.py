#-------------------------------------------------------------------------------
#
# Title:          Pull BLS Announcement Dates
#
# Author:         Matt Carl
#
# Date:           December 22, 2020
#
# Date Updated:
#
# Input:          https://www.bls.gov/schedule/., histreleases.pdf
#
# Output:         bls_announcement_dates.csv
#
#-------------------------------------------------------------------------------

#https://realpython.com/beautiful-soup-web-scraper-python/
import requests
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup # scraping HTML
import tabula # reading PDF data
import re
import math
from functools import reduce
import string
import os

path_in = "/Users/matthewcarl/Dropbox/research/ml_announcements/data/raw"
path_out = "/Users/matthewcarl/Dropbox/research/ml_announcements/data/final"

#-------------------------------------------------------------------------------
### 2008 - 2020 (consistent format, clean)
def macro_announcements1(URL):
  url=URL
  page=requests.get(URL)
  soup = BeautifulSoup(page.content, 'html.parser')
  #soup

  tab = soup.find_all('td', {'class':['date-cell', 'time-cell','desc-cell']})
  #tab

  date = []
  time = []
  desc = []
  for i in range(len(tab)):
    if i%3 == 0:
      date.append(tab[i].get_text())
    elif i%3 == 1:
      time.append(tab[i].get_text())
    else:
      desc.append(tab[i].get_text())

  announcements = pd.DataFrame([date, time, desc], index=['date', 'time', 'desc']).T

  return announcements

# Function call
url_list1 = ['https://www.bls.gov/schedule/2008/home.htm', 'https://www.bls.gov/schedule/2009/home.htm',
              'https://www.bls.gov/schedule/2010/home.htm', 'https://www.bls.gov/schedule/2011/home.htm',
              'https://www.bls.gov/schedule/2012/home.htm', 'https://www.bls.gov/schedule/2013/home.htm',
              'https://www.bls.gov/schedule/2014/home.htm', 'https://www.bls.gov/schedule/2015/home.htm',
              'https://www.bls.gov/schedule/2016/home.htm', 'https://www.bls.gov/schedule/2017/home.htm',
              'https://www.bls.gov/schedule/2018/home.htm', 'https://www.bls.gov/schedule/2019/home.htm',
              'https://www.bls.gov/schedule/2020/home.htm']

data1 = []
for k in range(len(url_list1)):
  data1.append(macro_announcements1(url_list1[k]))

data1 = pd.concat(data1)

#-------------------------------------------------------------------------------

### 1997 - 2007 (inconsistent format, messier)
def macro_announcements2(URL, Year):
  page=requests.get(URL)
  soup = BeautifulSoup(page.content, 'html.parser')

  tab = soup.find_all('pre')
  tab1=tab[0].get_text().split("\r\n")
  #tab1

  tab1 = [x.strip() for x in tab1 if x.strip()]
  #tab1

  # Depending on the year, need to delete different number of rows from header
  if Year == 1997 or Year == 1998:
    del tab1[0:5] # remove header
  elif 1999 <= Year <= 2007:
    del tab1[0:2] # remove header

  tab1 = [x for x in tab1 if x] # remove empty strings
  #tab1

  tab2 = []
  error_list = []
  for i in range(len(tab1)):
    tab2.append(re.split('\t|\t\t|   ', tab1[i]))
    for x in range(len(tab2[i])):
      if x > 1:
        tab2[i][x] = tab2[i][x].replace(' ','')
        tab2[i][x] = tab2[i][x].replace('  ','')
        tab2[i][x] = tab2[i][x].replace('   ','')

    tab2[i] = [x for x in tab2[i] if x]
    if len(tab2[i]) != 3:
      error_list.append(i)

  # Fix errors
  #error_list
  #tab2
  error_error_list = []
  for c in range(len(error_list)):
    i = error_list[c]
    if len(tab2[i]) < 3:
      tmp=[]
      for x in range(len(tab2[i])):
        tmp.append(re.split('\t|\t\t|  ', tab2[i][x]))
      tab2[i] = [tmp[0][0], tmp[0][1], tmp[1][0]]
    elif len(tab2[i]) > 3:
      for x in range(len(tab2[i])):
        if x >= 1: # Greater than or equal to pick up extraneous spaces appearing earlier
          tab2[i][x] = tab2[i][x].replace(' ','')
          tab2[i][x] = tab2[i][x].replace('  ','')
          tab2[i][x] = tab2[i][x].replace('   ','')
      tab2[i] = [x for x in tab2[i] if x]
  if len(tab2[i]) != 3:
    error_error_list.append(i)
    print("ERRORS REMAIN: CHECK CODE!!!")

  # Create data
  desc = []
  date = []
  time = []

  for i in range(len(tab2)):
    for j in range(len(tab2[i])):
      if j%3 == 0:
        desc.append(tab2[i][j])
      elif j%3 == 1:
        date.append(tab2[i][j])
      else:
        time.append(tab2[i][j])

  announcements = pd.DataFrame([date, time, desc], index =['date', 'time', 'desc']).T

  return announcements

# Function call
url_list2 = [#'https://www.bls.gov/schedule/1997/home.htm','https://www.bls.gov/schedule/1998/home.htm',
              #'https://www.bls.gov/schedule/1999/home.htm','https://www.bls.gov/schedule/2000/home.htm',
              'https://www.bls.gov/schedule/2001/home.htm','https://www.bls.gov/schedule/2002/home.htm',
              'https://www.bls.gov/schedule/2003/home.htm','https://www.bls.gov/schedule/2004/home.htm',
              'https://www.bls.gov/schedule/2005/home.htm','https://www.bls.gov/schedule/2006/home.htm',
              'https://www.bls.gov/schedule/2007/home.htm']
#year2 = [1997,1998,1999,2000,2001,2002,2003,2004,2005,2006,2007]
year2 = [2001,2002,2003,2004,2005,2006,2007]

data2 = []
for k in range(len(url_list2)):
  data2.append(macro_announcements2(url_list2[k], year2[k]))

data2 = pd.concat(data2)

#-------------------------------------------------------------------------------

def macro_announcements3(page=2, release="National Employment and Unemployment Estimates, "):
  table = tabula.read_pdf('histreleases.pdf', pages=page)
  df = table[0]

  month = []
  for i in range(len(df.iloc[0,0:13])):
    month.append(df.iloc[0,0:13][i])
  del(month[0])
  #month

  year = df.iloc[1,0:13][0].split("\r")
  #year

  months = []
  for i in range(1,len(df.iloc[1,0:13])):
    if isinstance(df.iloc[1,0:13][i],str) == True:
      months.append(df.iloc[1,0:13][i].split("\r"))
    else:
      months.append(["--"]*25)
  #months

  date=[]
  for a in range(len(months[1])):
    for m in range(len(months)):
      date.append(months[m][a])
  #date
  desc = []
  for y in range(len(year)):
    for m in range(len(month)):
      desc.append(release + month[m] + " " + year[y])
  #desc

  histrelease = pd.DataFrame([date, desc], index=['date', 'desc']).T

  return histrelease


### 1957 - 1996 (National Employment and Unemployment Estimates)
unemp = macro_announcements3(2, "National Employment and Unemployment Estimates, ")
#unemp

### 1953 - 1996 (CPI)
cpi = macro_announcements3(3, "Consumer Price Index, ")
#cpi

### 1971 - 1996 (PPI)
ppi = macro_announcements3(4, "Producer Price Index, ")
#ppi

### 1976 - 1996 (Employment Cost Index)
eci = macro_announcements3(5, "Employment Cost Index, ")
#eci

data3 = [unemp, cpi, ppi, eci]
data3 = pd.concat(data3)
#data3

#-------------------------------------------------------------------------------
### Clean data
# data1: all info available in date column. Just need to eliminate day of week, holidays
data1 = data1.reset_index()
del data1['index']

for i in range(len(data1)):
  data1.date[i] = data1.date[i].replace('Monday, ','').replace('Tuesday, ','').replace('Wednesday, ','').replace('Thursday, ','').replace('Friday, ','').replace('Saturday, ','').replace('Sunday, ','')

data1 = data1[~data1['desc'].isin(['Independence Day','Memorial Day','Labor Day','Columbus Day','Veterans Day','Thanksgiving Day','Christmas Day','''New Year's Day''','Birthday of Martin Luther King, Jr.',''''Washington's Birthday'''])]
data1['datetime'] = data1.date + " " + data1.time
data1.index = pd.to_datetime(data1.datetime)
#del data1['date']
del data1['time']
del data1['datetime']
#data1

#--------------------------------
# data2: Need to extract year from desc column, clean date column
data2["date"] = [el.replace(".", " ").replace(",", ", ").replace("Jan","Jan ").replace("Feb","Feb ").replace("March","March ").replace("April","April ").replace("May","May ").replace("June","June ").replace("July","July ").replace("Aug","Aug ").replace("Sept","Sept ").replace("Oct","Oct ").replace("Nov","Nov ").replace("Dec","Dec ").lstrip().rstrip().replace("  ", " ")
 for el in data2["date"]]
data2["date"] = [el.replace("  ", " ") for el in data2["date"]]

data2 = data2.reset_index()
del data2['index']

data2['date'] = data2.date.apply(lambda x: x.replace("*","").replace("**","").replace("***","").replace("20001","2001"))
data2['desc'] = data2.desc.apply(lambda x: x.replace("(p"," (p").replace("(r"," (r"))

tmp_str = data2.desc.apply(lambda x: x.split())
#tmp_str
years = [j for i in tmp_str for j in i if j.isdigit()]

has_year = [data2.date[i].__contains__(',') for i in range(len(data2.date))]

for i in range(len(data2.date)):
  if not has_year[i]:
      data2.date[i] = data2.date[i] + ", " + years[i]

#data2.date[511]
#data2.date[511]='Jan 10, 2001'
i = data2[data2.date == 'Jan 10, 20001'].index[0]
data2.date[i] = 'Jan 10, 2001'

data2['datetime'] = data2.date + " " + data2.time

data2.datetime = pd.to_datetime(data2.datetime)
data2.date = pd.to_datetime(data2.date)
#data2.date
#data2.datetime
data2.index = pd.to_datetime(data2.datetime)
del data2['datetime']
#del data2['date']
del data2['time']
#data2

#--------------------------------
# data3
data3 = data3[data3['date'] != "--"]
data3 = data3.reset_index()
del data3['index']

current = ["1January 31, 1996", "June 181", "July 303", "1February 27", "3April 30"]
correct = ["January 31, 1996" , "June 18",  "July 30",  "February 27",  "April 30"]
for i in range(len(current)):
  k = data3[data3.date == current[i]].index[0]
  data3['date'][k] = correct[i]

tmp_str = data3.desc.apply(lambda x: x.split())
#tmp_str
years = [j for i in tmp_str for j in i if j.isdigit()]

has_year = [data3.date[i].__contains__(',') for i in range(len(data3.date))]

for i in range(len(data3.date)):
  if not has_year[i]:
      data3.date[i] = data3.date[i] + ", " + years[i]

data3.index = pd.to_datetime(data3.date)
#del data3['date']

#data3
#-------------------------------------------------------------------------------
### Merge all announcements
data = [data3, data2, data1]
data = pd.concat(data)
data = data.sort_index()
#data

#-------------------------------------------------------------------------------
### Create indicators for announcements
# Employment
emp=[]
for i in range(len(data.desc)):
  if 'National Employment and Unemployment Estimates' in data.desc[i]:
    emp.append(1)
  elif 'Employment Situation' in data.desc[i]:
    emp.append(1)
  else:
    emp.append(np.nan)
data['emp_ann'] = emp


# CPI
cpi=[]
for i in range(len(data.desc)):
  if 'Consumer Price Index' in data.desc[i]:
    cpi.append(1)
  else:
    cpi.append(np.nan)
data['cpi_ann'] = cpi

#PPI
ppi=[]
for i in range(len(data.desc)):
  if 'Producer Price Index' in data.desc[i]:
    ppi.append(1)
  else:
    ppi.append(np.nan)
data['ppi_ann'] = ppi

# ECI
eci=[]
for i in range(len(data.desc)):
  if 'Employment Cost Index' in data.desc[i]:
    eci.append(1)
  else:
    eci.append(np.nan)
data['eci_ann'] = eci

# US Import and Export Price Index
mxpi=[]
for i in range(len(data.desc)):
  if 'U.S. Import and Export Price Indexes' in data.desc[i]:
    mxpi.append(1)
  else:
    mxpi.append(np.nan)
data['mxpi_ann'] = mxpi

# Real Earnings
re=[]
for i in range(len(data.desc)):
  if 'Real Earnings' in data.desc[i]:
    re.append(1)
  else:
    re.append(np.nan)
data['real_earnings_ann'] = re

# Metropolitican Area Employment
metro_emp=[]
for i in range(len(data.desc)):
  if 'Metropolitan Area Employment and Unemployment' in data.desc[i]:
    metro_emp.append(1)
  else:
    metro_emp.append(np.nan)
data['metro_emp_ann'] = metro_emp

# State and Regional Employment
state_emp=[]
for i in range(len(data.desc)):
  if 'State Employment and Unemployment' in data.desc[i]:
    state_emp.append(1)
  elif 'Regional and State Employment and Unemployment' in data.desc[i]:
    state_emp.append(1)
  else:
    state_emp.append(np.nan)
data['state_emp_ann'] = state_emp

# Productivity and Costs
pc=[]
for i in range(len(data.desc)):
  if 'Productivity and Costs' in data.desc[i]:
    pc.append(1)
  else:
    pc.append(np.nan)
data['prod_costs_ann'] = pc

#-------------------------------------------------------------------------------
### Delete duplicates
"""
len(data)
emp_ann = data.drop_duplicates(subset=['date','emp_ann'])[['date','emp_ann','desc']].dropna(how='any')
cpi_ann = data.drop_duplicates(subset=['date','cpi_ann'])[['date','cpi_ann','desc']].dropna(how='any')
ppi_ann = data.drop_duplicates(subset=['date','ppi_ann'])[['date','ppi_ann','desc']].dropna(how='any')
eci_ann = data.drop_duplicates(subset=['date','eci_ann'])[['date','eci_ann','desc']].dropna(how='any')
mxpi_ann = data.drop_duplicates(subset=['date','mxpi_ann'])[['date','mxpi_ann','desc']].dropna(how='any')
real_earnings_ann = data.drop_duplicates(subset=['date','real_earnings_ann'])[['date','real_earnings_ann','desc']].dropna(how='any')
metro_emp_ann = data.drop_duplicates(subset=['date','metro_emp_ann'])[['date','metro_emp_ann','desc']].dropna(how='any')
state_emp_ann = data.drop_duplicates(subset=['date','state_emp_ann'])[['date','state_emp_ann','desc']].dropna(how='any')
prod_costs_ann = data.drop_duplicates(subset=['date','prod_costs_ann'])[['date','prod_costs_ann','desc']].dropna(how='any')

df = [emp_ann, cpi_ann, ppi_ann, eci_ann, mxpi_ann, real_earnings_ann,
      metro_emp_ann, state_emp_ann, prod_costs_ann]

for i in range(len(df)):
  del df[i]['date']

data_final = reduce(lambda l,r: pd.merge(l,r,left_index=True, right_index=True, how='outer'), df).fillna(np.nan)
data_final['desc_final'] = data_final[['desc_x', 'desc_y']].apply(
    lambda x: ','.join(x.dropna().astype(str)), axis=1)
data_final['desc_final']
del data_final['desc_x']
del data_final['desc_y']
del data_final['desc']
"""

data = data.dropna(subset=['emp_ann','cpi_ann','ppi_ann','eci_ann','mxpi_ann','real_earnings_ann','metro_emp_ann','state_emp_ann','prod_costs_ann'],how='all')
data = data.sort_index()

#data

#-------------------------------------------------------------------------------
### Output data
os.chdir(path_out)
data.to_excel('bls_announcement_dates.xlsx', index=True, index_label='Datetime', na_rep='NULL')
