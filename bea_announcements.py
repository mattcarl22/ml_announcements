#-------------------------------------------------------------------------------
#
# Title:          Pull BEA Announcement Dates (GDP)
#
# Author:         Matt Carl
#
# Date:           January 3, 2021
#
# Date Updated:
#
# Input:          https://www.bea.gov/news/archive
#
# Output:         gdp_announcement_dates.csv
#
#-------------------------------------------------------------------------------

import requests
import pandas as pd
from bs4 import BeautifulSoup # scraping HTML
import tabula # reading PDF data
import re
import math
import string
import os

path_in = "/Users/matthewcarl/Dropbox/research/ml_announcements/data/raw"
path_out = "/Users/matthewcarl/Dropbox/research/ml_announcements/data/final"

#-------------------------------------------------------------------------------

def gdp_announcements(URL):
  #url = 'https://www.bea.gov/news/archive?field_related_product_target_id=451&created_1=All&title='
  #URL = url
  page=requests.get(URL)

  soup = BeautifulSoup(page.content, 'html.parser')
  #soup

  tab = soup.find_all('tr', {'class':'release-row'})
  #tab

  data = []
  for i in range(len(tab)):
    data.append(tab[i].get_text().lstrip().replace('  ', ' ').rstrip().split("\n"))

  desc = []
  date = []
  for i in range(len(tab)):
    desc.append(data[i][0])
    date.append(data[i][1])

  announcements = pd.DataFrame([date, desc], index=['date', 'desc']).T

  return announcements

# Function call
url_list = ['https://www.bea.gov/news/archive?field_related_product_target_id=451&created_1=All&title=',
            'https://www.bea.gov/news/archive?field_related_product_target_id=451&created_1=All&title=&page=1',
            'https://www.bea.gov/news/archive?field_related_product_target_id=451&created_1=All&title=&page=2',
            'https://www.bea.gov/news/archive?field_related_product_target_id=451&created_1=All&title=&page=3',
            'https://www.bea.gov/news/archive?field_related_product_target_id=451&created_1=All&title=&page=4',
            'https://www.bea.gov/news/archive?field_related_product_target_id=451&created_1=All&title=&page=5',
            'https://www.bea.gov/news/archive?field_related_product_target_id=451&created_1=All&title=&page=6',
            'https://www.bea.gov/news/archive?field_related_product_target_id=451&created_1=All&title=&page=7',
            'https://www.bea.gov/news/archive?field_related_product_target_id=451&created_1=All&title=&page=8',
            'https://www.bea.gov/news/archive?field_related_product_target_id=451&created_1=All&title=&page=9',
            'https://www.bea.gov/news/archive?field_related_product_target_id=451&created_1=All&title=&page=10',
            'https://www.bea.gov/news/archive?field_related_product_target_id=451&created_1=All&title=&page=11',
            'https://www.bea.gov/news/archive?field_related_product_target_id=451&created_1=All&title=&page=12',
            'https://www.bea.gov/news/archive?field_related_product_target_id=451&created_1=All&title=&page=13',
            'https://www.bea.gov/news/archive?field_related_product_target_id=451&created_1=All&title=&page=14']

df = []
for k in range(len(url_list)):
  df.append(gdp_announcements(url_list[k]))

gdp_announcements = pd.concat(df)

# Export data
os.chdir(path_out)
gdp_announcements.to_csv(r'gdp_announcement_dates.csv', index=False)
