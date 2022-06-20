"""
This scripts is basically the same as `match_1`. The difference is that, after analyzing the no_match and no_results 
	of `match_1`, I :
		- For 64 papers, I query them by DOI in the first place because their title queries were successful but wrong
		- For 1 paper, their correct results are not the first result, I manually checked their correct indexes. 

input: vispd_plus_good_papers, vispubdata_plus

"""

import requests
import csv
import pandas as pd
import random
import re
import time
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import sys
import time

VISPD_PLUS_GOOD_PAPERS = sys.argv[1]
VISPUBDATA_PLUS = sys.argv[2]
VISPD_OPENALEX_MATCH_2 = sys.argv[3]
TITEL_QUERY_EMPTY_DOI_QUERY_404_2 = sys.argv[4]
TITLE_QUERY_404_2 = sys.argv[5]
DOI_QUERY_404_2 = sys.argv[6]

def read_txt(INPUT):
	"""read txt files and return a list
	"""
	raw = open(INPUT, "r")
	reader = csv.reader(raw)
	allRows = [row for row in reader]
	data = [i[0] for i in allRows]
	return data

def get_dicts(VISPUBDATA_PLUS):
	# get year_dict and title_dict
	vispd_plus = pd.read_csv(VISPUBDATA_PLUS)
	dois = vispd_plus.loc[:, "DOI"].tolist()
	titles = vispd_plus.loc[:, "Title"].tolist()
	years = vispd_plus.loc[:, "Year"].tolist()
	doi_year_dict = dict(zip(dois, years))
	doi_title_dict = dict(zip(dois, titles))
	return [doi_year_dict, doi_title_dict]

def get_title_query_response(doi):
	title_original = doi_title_dict[doi]
	title = re.sub(r'\:|\?|\&|\,', '', title_original)
	response = requests.get(
		'https://api.openalex.org/works?filter=title.search:' + title)
	return response

def check_results_count(response):
	j = response.json()
	count = j['meta']['count']
	return j, count 

def get_doi_query_response(doi):
	response = requests.get("https://api.openalex.org/works/doi:" + doi)
	return response

def get_paper_dict_from_json_result(j, doi):
	openalex_id = j['id']
	openalex_title = j['display_name']
	openalex_year = j['publication_year']
	openalex_doi = j['doi']
	venue = j['host_venue']
	openalex_venue = venue['id']
	openalex_url = venue['url']
	openalex_journal = venue['display_name']
	openalex_publisher = venue['publisher']
	openalex_first_page = j['biblio']['first_page']
	openalex_last_page = j['biblio']['last_page']
	paper_dict = {
		'Year': doi_year_dict[doi],
		'DOI': doi,
		'Title': doi_title_dict[doi],
		'OpenAlex Year': openalex_year,
		'OpenAlex ID': openalex_id,
		'OpenAlex Title': openalex_title,
		'OpenAlex DOI': openalex_doi,
		'OpenAlex URL': openalex_url,
		'OpenAlex Venue': openalex_venue,
		'OpenAlex Journal': openalex_journal,
		'OpenAlex Publisher': openalex_publisher,
		'OpenAlex First Page': openalex_first_page,
		'OpenAlex Last Page': openalex_last_page,
	}
	return paper_dict

def get_empty_paper_dict(doi):
	paper_dict = {
		'Year': doi_year_dict[doi],
		'DOI': doi,
		'Title': doi_title_dict[doi],
	}
	return paper_dict

def update_paper_dict_list(doi, doi_index):
	if doi not in to_query_by_doi:
		# query title first:
		response = get_title_query_response(doi)
		# if status code is in retry_code, retry:
		while response.status_code in retry_code:
			print(f'title query for {doi_index} : {doi} is having errors, error status code is {response.status_code}, retrying...')
			time.sleep(1)
			response = get_title_query_response(doi)
		# if title query succeeds:
		if response.status_code == 200:
			# get json and check results count:
			j = check_results_count(response)[0]
			count = check_results_count(response)[1]
			# if count is non-zero:
			if count > 0:
				# if doi not in special_result_index_dict, use index of 0
				if doi not in list(special_result_index_dict.keys()):
					first_result = j['results'][0]
					paper_dict = get_paper_dict_from_json_result(first_result, doi)
				else:
					correct_index = special_result_index_dict[doi]
					correct_result = j['results'][correct_index]
					paper_dict = get_paper_dict_from_json_result(correct_result, doi)
			# if count is zero, use doi query instead
			else:
				# get doi query response:
				response2 = get_doi_query_response(doi)
				# if status code is in retry_code, retry:
				while response2.status_code in retry_code:
					print(f'doi query for {doi_index} : {doi} is having errors, error status code is {response2.status_code}, retrying...')
					time.sleep(1)
					response2 = get_doi_query_response(doi)
				# if doi query succeeds:
				if response2.status_code == 200:
					j2 = response2.json()
					paper_dict = get_paper_dict_from_json_result(j2, doi)
				# if doi query fails, add the list to no_result list
				else:
					# empty title query results and bad doi query
					error_status_code.append(response2.status_code)
					title_query_empty_doi_query_404_list.append(doi)
					paper_dict = get_empty_paper_dict(doi)
					print(f'doi query is fails for {doi_index} : {doi}, whose title is {doi_title_dict[doi]}')
	
		# if title query fails:	
		else:
			title_query_404_list.append(doi)
			error_status_code.append(response.status_code)
			paper_dict = get_empty_paper_dict(doi)
			print(f'title query fails for {doi_index} : {doi_title_dict[doi]}')
	else:
		response0 = get_doi_query_response(doi)
		# if status code is in retry_code, retry
		while response0.status_code in retry_code:
			print(f'doi query for {doi_index} : {doi} is having errors, error status code is {response0.status_code}, retrying...')
			time.sleep(3)
			response0 = get_doi_query_response(doi)
		# if doi query succeeds:
		if response0.status_code == 200:
			j0 = response0.json()
			paper_dict = get_paper_dict_from_json_result(j0, doi)
		# if doi query fails:
		else:
			error_status_code.append(response0.status_code)
			doi_query_404_list.append(doi)
			paper_dict = get_empty_paper_dict(doi)
			print(f'doi query fails for {doi_index} : {doi}')
	paper_dict_list.append(paper_dict)
	
def main(DOIS):
	for doi in DOIS:
		doi_index = DOIS.index(doi) + 1
		update_paper_dict_list(doi, doi_index)
		print(f'{doi_index} is done')
		time.sleep(0.5)
	print(list(set(error_status_code)))

if __name__ == '__main__':
	# note on 2022-01-21: it's not a bug here but it might be error-prone:
	# i defined s here and then i used it direclty in the function of `main`
	# without "importing" the parameter, like `main(vispd_plus_good_papers, s)`
	# it's working, but as I said, it might be error prone
	vispd_plus_good_papers = read_txt(VISPD_PLUS_GOOD_PAPERS)
	doi_year_dict = get_dicts(VISPUBDATA_PLUS)[0]
	doi_title_dict = get_dicts(VISPUBDATA_PLUS)[1]
	retry_code = [ 500, 502, 503, 504, 429]
	paper_dict_list = []
	title_query_empty_doi_query_404_list = []
	title_query_404_list = []
	doi_query_404_list = []
	error_status_code = []
	to_query_by_doi = [
		'10.1109/VISUAL.2001.964489',
		'10.1109/VISUAL.1996.568113',
		'10.1109/VISUAL.1999.809896',
		'10.1109/VISUAL.1991.175771',
		'10.1109/VISUAL.1998.745302',
		'10.1109/VISUAL.1993.398868',
		'10.1109/INFVIS.2005.1532128',
		'10.1109/VISUAL.1993.398859',
		'10.1109/VISUAL.1991.175795',
		'10.1109/VISUAL.2003.1250401',
		'10.1109/VISUAL.1991.175789',
		'10.1109/VISUAL.2000.885739',
		'10.1109/TVCG.2014.2346922',
		'10.1109/VISUAL.1999.809871',
		'10.1109/VISUAL.1996.567807',
		'10.1109/VISUAL.2000.885692',
		'10.1109/VISUAL.1991.175777',
		'10.1109/VISUAL.1998.745315',
		'10.1109/VISUAL.1997.663909',
		'10.1109/VISUAL.2000.885697',
		'10.1109/VISUAL.2001.964504',
		'10.1109/TVCG.2006.168',
		'10.1109/TVCG.2007.70617',
		'10.1109/VISUAL.1997.663910',
		'10.1109/VISUAL.1997.663931',
		'10.1109/VISUAL.2002.1183792',
		'10.1109/VISUAL.1992.235201',
		'10.1109/VISUAL.1996.568128',
		'10.1109/VISUAL.1997.663923',
		'10.1109/VAST.2011.6102441',
		'10.1109/VISUAL.2000.885732',
		'10.1109/VISUAL.2001.964522',
		'10.1109/VISUAL.2005.1532812',
		'10.1109/VISUAL.1998.745350',
		'10.1109/INFVIS.2001.963282',
		'10.1109/VISUAL.1995.480804',
		'10.1109/VISUAL.2005.1532847',
		'10.1109/INFVIS.1996.559229',
		'10.1109/VISUAL.2000.885738',
		'10.1109/VISUAL.1991.175800',
		'10.1109/VISUAL.1993.398865',
		'10.1109/VISUAL.1993.398866',
		'10.1109/VISUAL.1998.745348',
		'10.1109/VISUAL.1993.398867',
		'10.1109/VISUAL.1997.663925',
		'10.1109/VISUAL.1993.398900',
		'10.1109/VISUAL.1992.235181',
		'10.1109/VISUAL.1992.235195',
		'10.1109/VISUAL.2000.885719',
		'10.1109/VISUAL.1991.175816',
		'10.1109/VISUAL.1990.146414',
		'10.1109/VISUAL.1993.398861',
		'10.1109/VISUAL.1993.398872',
		'10.1109/VISUAL.1994.346292',
		'10.1109/VISUAL.1994.346295',
		'10.1109/VISUAL.1994.346297',
		'10.1109/VISUAL.1994.346301',
		'10.1109/VISUAL.1999.809913',
		'10.1109/VISUAL.2001.964546',
		'10.1109/VISUAL.2003.1250404',
		'10.1109/TVCG.2014.2346442',
		'10.1109/TVCG.2020.3028948',
		'10.1109/TVCG.2020.3030363',
		'10.1109/TVCG.2020.3030364',
		'10.1109/tvcg.2021.3114784',
		'10.1109/tvcg.2021.3114780',
		'10.1109/tvcg.2021.3114782',
		'10.1109/tvcg.2021.3114783',
		'10.1109/tvcg.2021.3114836',
		'10.1109/TVCG.2021.3064037',
		'10.1109/TVCG.2021.3114849',
		'10.1109/TVCG.2021.3114842',
		'10.1109/TVCG.2021.3114766',
		'10.1109/TVCG.2021.3114777'
	]
	special_result_index_dict = {
		'10.1109/VISUAL.1992.235194': 4,
	}
	main(vispd_plus_good_papers)

paper_df = pd.DataFrame(paper_dict_list)

paper_df.to_csv(VISPD_OPENALEX_MATCH_2, index=False)

with open(TITEL_QUERY_EMPTY_DOI_QUERY_404_2, 'w') as f:
	for doi in title_query_empty_doi_query_404_list:
		f.write("%s\n" % doi)

with open(TITLE_QUERY_404_2, 'w') as f:
	for doi in title_query_404_list:
		f.write("%s\n" % doi)

with open(DOI_QUERY_404_2, 'w') as f:
	for doi in doi_query_404_list:
		f.write("%s\n" % doi)