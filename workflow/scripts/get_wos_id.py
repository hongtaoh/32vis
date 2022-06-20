"""In this script, for each DOI in vispd plus good papers, I tried to get its corresponding Web of Science ID
"""

import pandas as pd
import urllib
import requests
from bs4 import BeautifulSoup
import re
import csv
import random
import numpy as np
import time
import sys

INPUT = sys.argv[1]
OUT_FNAME = sys.argv[2]

def get_wos_id_from_doi(doi):
	url = f'http://ws.isiknowledge.com/cps/openurl/service?url_ver=Z39.88-2004&rft_id=info:doi/{doi}'
	headers = {
		"user-agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36",
	}
	response = requests.get(url=url, headers=headers)
	wos_url = response.history[-1].url
	wos_id_list = re.findall(r'(?<=2FWOS%3A)(.*)(?=%3F)', wos_url)
	if wos_id_list:
		wos_id = wos_id_list[0]
	else:
		wos_id = np.NaN
	doi_wos_dict = {
		'DOI': doi,
		'WOS ID': wos_id
	}
	doi_wos_dict_list.append(doi_wos_dict)

def get_dois(INPUT):
	good_dois = open(INPUT, 'r')
	reader = csv.reader(good_dois)
	allRows = [row for row in reader]
	dois = [i[0] for i in allRows]
	return dois 

def build_df_from_dict_list(df, dict_list):
	"""build df from a list of dictionaries
	
	Arguments:
	   df: an empty df you just initiated
	   
	   dict_list: a list of dictionaries containing data you want to form a df
	
	Returns:
	  The updated df
	"""
	for i in dict_list:
		df_1 = pd.DataFrame([i])
		df = df.append(df_1, ignore_index=True)
	return df

def main():
	for doi in dois:
		get_wos_id_from_doi(doi)
		time.sleep(2+random.uniform(0, 2))
		print(f'{dois.index(doi) + 1} is done')

if __name__ == '__main__':
	# initiate a list of dicts
	doi_wos_dict_list = []
	dois = get_dois(INPUT)
	main()
	# initiate a dataframe 
	doi_wos_df_initiate = pd.DataFrame(columns=['DOI', 'WOS ID'])
	doi_wos_df = build_df_from_dict_list(
		doi_wos_df_initiate, doi_wos_dict_list)
	doi_wos_df.to_csv(OUT_FNAME, index=False)
