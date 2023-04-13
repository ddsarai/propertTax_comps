'''
File: update_ptaxData.py
This program checks to see if any new property tax data germane to the project has been added to the government websites of Ontario, British Columbia, and Alberta.

It then downloads any excel spreadsheet that are not included in the project data directory
'''

# Note:  need to cleanup/refactor code

import requests
from bs4 import BeautifulSoup as bs
from datetime import datetime
import pandas as pd
import os
import sys
from zipfile import ZipFile as zfile
def checkConnect(url):
    try:
        soup = bs(requests.get(url, headers=headers).content, 'html.parser')
        return soup
    except requests.exceptions.ConnectionError:
        if 'alberta' in url:
            with open('ErrorLog.txt', 'a+') as f:
                f.write(f'\nConnectionError AB data on {datetime.now()}')
                f.close()
            sys.exit('AB data not available')
        elif 'bc' in url:
            with open('ErrorLog.txt', 'a+') as f:
                f.write(f'\nConnectionError BC data on {datetime.now()}')
                f.close()
            sys.exit('BC data not available')
        else:
            with open('ErrorLog.txt', 'a+') as f:
                f.write(f'\nConnectionError ON data on {datetime.now()}')
                f.close()
            sys.exit('ON data not available')

# def dload_list(data):
#     #finish dload function
#     if key +'.xlsx' not in files:

headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:106.0) Gecko/20100101 Firefox/106.0','Accept': '*/*', 'Accept-Encoding': 'gzip, deflate, br', 'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8'}

ON_url = 'https://efis.fma.csc.gov.on.ca/fir/index.php/en/open-data/fir-by-schedule-and-year/' 
BC_url = 'https://www2.gov.bc.ca/gov/content/governments/local-governments/facts-framework/statistics/tax-rates-tax-burden'
AB_url = 'https://open.alberta.ca/opendata/municipal-financial-and-statistical-data'

ON_soup = checkConnect(ON_url)

on_files = ON_soup.find_all('a', {'class':'download-wrap'})

on_ptax_data={}
for file in on_files:
    if file.attrs.get('href')[-6:-4] != '22':
        continue
    else:
        key = file.attrs.get('href')[-18:-4]
        val = file.attrs.get('href')
        on_ptax_data[key] = val
        

os.chdir('data/ON_Ptax/')
files=os.listdir()

download = []

for key in on_ptax_data:
    if key +'.xlsx' not in files:
        download.append(on_ptax_data[key])
    # elif key + '.xls' not in files:
    #     download.append(on_ptax_data[key])
    else:
        continue

for url in download:
    file_name = url.split('/')[-1]
    response = requests.get(url, stream=True)
    with open(file_name, 'wb') as f:
        f.write(response.content)
    with zfile(file_name, 'r')as zObj:
        zObj.extractall()


bc_soup = checkConnect(BC_url)

bc_files = bc_soup.find('div', {'id':'c86ca455b2188dbf9b8a5a1b045ded28'}).find_all('a')
bc_ptax_data={}
for file in bc_files:
    if len(file.attrs.get('href').split('/')[-1]) == 21:
        key = file.attrs.get('href')[-21:]
        val = file.attrs.get('href')
        bc_ptax_data[key] = val
    else:
        key = file.attrs.get('href')[-20:]
        val = file.attrs.get('href')
        bc_ptax_data[key] = val
print(os.getcwd())
os.chdir('../BC_Ptax')

download = []
for key in bc_ptax_data:   
    if key not in files :
        download.append(bc_ptax_data[key])
    else:
         continue
    
for url in download:
    file_name = url.split('/')[-1]
    url = 'https://www2.gov.bc.ca/' + url
    response = requests.get(url,headers=headers, stream=True)
    with open(file_name, 'wb') as f:
        f.write(response.content)

AB_soup = checkConnect(AB_url)

ab_files = AB_soup.find_all('a', {'class':'heading'})


ab_ptax_data={}
for file in ab_files:
    href = file.attrs.get('href')
    if (href[-3:] == 'lsx') & (href[-19] != 'f'):
        key = href[-19:-5]
        val = href
        ab_ptax_data[key] = val
    elif href[-19] == 'f':
        key = href[-24:-5]
        val = href
        ab_ptax_data[key] = val
    else:
        continue

os.chdir('../AB_Ptax/')
download = []
files = os.listdir()
for key in ab_ptax_data:
    if key + '.xlsx' not in files:
        download.append(ab_ptax_data[key])
    else:
        continue

for url in download:
    file_name = url.split('/')[-1]
    response = requests.get(url, stream=True)
    with open(file_name,'wb') as f:
        f. write(response.content)

#AB update only checks files starting with 2017