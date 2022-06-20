"""In this script, I get author data and IEEE paper title by scraping IEEE

input: 
	- papers_to_study for the DOIS
	- `vispubdata_plus` for doi_year/title_dict

output: 
	- ieee author data
	- ieee paper data (with ieee paper title)
	- problem dois, where I failed to get author data

"""

import pandas as pd
from bs4 import BeautifulSoup
import requests, lxml
import json
import numpy as np
import sys
import random
import time
from io import StringIO
from html.parser import HTMLParser
import re

PAPERS_TO_STUDY = sys.argv[1]
VISPUBDATA_PLUS = sys.argv[2]
IEEE_AUTHOR_DF = sys.argv[3]
IEEE_PAPER_DF = sys.argv[4]
PROBLEM_DOIS = sys.argv[5]

def get_dicts(VISPUBDATA_PLUS):
	# get year_dict and title_dict
	vispd_plus = pd.read_csv(VISPUBDATA_PLUS)
	dois = vispd_plus.loc[:, "DOI"].tolist()
	titles = vispd_plus.loc[:, "Title"].tolist()
	years = vispd_plus.loc[:, "Year"].tolist()
	doi_year_dict = dict(zip(dois, years))
	doi_title_dict = dict(zip(dois, titles))
	return doi_year_dict, doi_title_dict

def get_response(URL):
	response = requests.get(url=URL, headers=headers)
	while response.status_code != 200:
		print('response status code is not 200. retrying now...')
		time.sleep(5)
		response = requests.get(url=URL, headers=headers)
	return response 

def get_soup(RESPONSE):
	html = RESPONSE.text
	soup = BeautifulSoup(html, 'lxml')
	return soup 

def get_j(DOI, SOUP):
	if DOI != '10.1109/VIS.1999.10000':
		str = SOUP.find_all('script')[11].string.rsplit(
			'xplGlobal.document.metadata=')[1].rsplit(
			'xplGlobal.document.userLoggedIn=')[0]

		# delete anything after the last `}`
		str = str.replace(re.findall(r'[^\}]+$', str)[0], '')
		j = json.loads(str)
	else:
		j = None
	return j

# scrip html tags and entities in titles
# source: https://stackoverflow.com/a/925630
class MLStripper(HTMLParser):
	def __init__(self):
		super().__init__()
		self.reset()
		self.strict = False
		self.convert_charrefs= True
		self.text = StringIO()
	def handle_data(self, d):
		self.text.write(d)
	def get_data(self):
		return self.text.getvalue()

def strip_tags(html):
	s = MLStripper()
	s.feed(html)
	return s.get_data()

# def get_ieee_title(J):
# 	# get ieee paper title
# 	title_raw = J['title']
# 	title = strip_tags(title_raw)
# 	return title

def update_paper_dict_list(J, DOI):
	if DOI != '10.1109/VIS.1999.10000':
		title_raw = J['title']
		ieee_title = strip_tags(title_raw)
		ieee_doi = J['doi']
	else:
		ieee_title = doi_title_dict[DOI]
		ieee_doi = DOI
	paper_dict = {
		'Year': doi_year_dict[DOI],
		'DOI': DOI,
		'Title': doi_title_dict[DOI],
		'IEEE Title': ieee_title,
		'IEEE DOI': ieee_doi,
	}
	paper_dict_list.append(paper_dict)

def update_author_dict_list(J, DOI):
	AUTHOR_JSON = J['authors']
	for i in AUTHOR_JSON:
		try:
			first_name = i['firstName']
		except:
			first_name = None
		try:
			last_name = i['lastName']
		except:
			last_name = None
		try:
			author_name = i['name']
		except:
			author_name = None
		author_num = len(AUTHOR_JSON)
		author_position = AUTHOR_JSON.index(i) + 1
		try:
			affiliation_element = i['affiliation']
			affiliation_name = affiliation_element[0]
			affiliation_num = len(affiliation_element)
			one_affiliation = True if affiliation_num == 1 else False
		except:
			affiliation_name = None
			affiliation_num = None
			one_affiliation = None
		try:
			author_id = 'https://ieeexplore.ieee.org/author/' + i['id']
		except:
			author_id = None
		author_dict = {
			'Year': doi_year_dict[DOI],
			'DOI': DOI,
			'Title': doi_title_dict[DOI],
			# 'IEEE Title': IEEE_TITLE,
			# 'First Name': first_name,
			# 'Last Name': last_name,
			'Number of Authors': author_num,
			'Author Position': author_position,
			'Author Name': author_name,
			'Author ID': author_id,
			'Author Affiliation': affiliation_name,
			# 'Number of Affiliations': affiliation_num,
			'One Affiliation': one_affiliation,
		}
		author_dict_list.append(author_dict)

def get_empty_author_dict(DOI):
	author_dict = {
		'Year': doi_year_dict[DOI],
		'DOI': DOI,
		'Title': doi_title_dict[DOI],
	}
	author_dict_list.append(author_dict)

def main(DOIS):
	for DOI in DOIS:
		doi_index = DOIS.index(DOI) + 1
		url = 'https://doi.org/' + DOI
		response = get_response(url)
		soup = get_soup(response)
		j = get_j(DOI, soup)
		update_paper_dict_list(j, DOI)
		try:
			if DOI != '10.1109/VIS.1999.10000':
				update_author_dict_list(j, DOI)
			else:
				get_empty_author_dict(DOI)
		except:
			problem_dois_list.append(DOI)
			print(f'something wrong with {DOI}')
		time.sleep(0.4+random.uniform(0, 0.4)) 
		print(f'{doi_index} is done')

if __name__ == '__main__':
	PAPERS = pd.read_csv(PAPERS_TO_STUDY, header=None)
	DOIS = PAPERS[0].tolist()
	random_dois = random.sample(DOIS, 10)
	random_dois.append('10.1109/VIS.1999.10000')
	doi_year_dict, doi_title_dict = get_dicts(VISPUBDATA_PLUS)
	headers = {
	'User-agent':
	'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.19582'
	}
	author_dict_list = []
	paper_dict_list = []
	problem_dois_list = []
	# main(random_dois)
	main(DOIS)
	author_df = pd.DataFrame(author_dict_list)
	paper_df = pd.DataFrame(paper_dict_list)
	author_df.to_csv(IEEE_AUTHOR_DF, index=False)
	paper_df.to_csv(IEEE_PAPER_DF, index=False)
	with open(PROBLEM_DOIS, 'w') as f:
		for doi in problem_dois_list:
			f.write("%s\n" % doi)
