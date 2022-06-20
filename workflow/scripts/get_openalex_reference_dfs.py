""" This script generates dataframes for reference papers

input: openalex_reference_df

output: openalex_reference paper_df, author_df, concept_df

"""

import pandas as pd 
import numpy as np 
import requests
import random
import re 
import sys 
import time 
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

OPENALEX_REFERENCE_DF = sys.argv[1]
OPENALEX_REFERENCE_PAPER_DF_UNIQUE = sys.argv[2]
OPENALEX_REFERENCE_AUTHOR_DF_UNIQUE = sys.argv[3]
OPENALEX_REFERENCE_CONCEPT_DF_UNIQUE = sys.argv[4]
OPENALEX_REFERENCE_PAPER_DF = sys.argv[5]
OPENALEX_REFERENCE_AUTHOR_DF = sys.argv[6]
OPENALEX_REFERENCE_CONCEPT_DF = sys.argv[7]
OPENALEX_REFERENCE_ERROR_DF = sys.argv[8]

def get_unique_ref_urls(ref_df): # ref_df here is OPENALEX_REFERENCE_DF
	# returns a list: unique reference paper urls
	ref = pd.read_csv(ref_df).dropna(subset=['Number of References'])
	unique_ref_urls = list(set(ref.Reference.tolist()))
	return ref, unique_ref_urls

def get_s():
	# set retry if status codes in [ 500, 502, 503, 504, 429]
	# als return headers
	s = requests.Session()
	retries = Retry(total=5,
		backoff_factor=0.1,
		status_forcelist=[ 500, 502, 503, 504, 429],
	)
	s.mount('http://', HTTPAdapter(max_retries=retries))
	headers = {
	"user-agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36",
	'Accept': 'application/json',
	}
	return s, headers

def get_paper_dict_from_json_result(j, url, paper_dict_list):
	"""returns a dict 
	"""
	authors = j['authorships']
	num_authors = len(authors)
	concepts = j['concepts']
	num_concepts = len(concepts)
	openalex_id = re.sub('https://openalex.org/', '', j['id'])
	openalex_title = j['display_name']
	openalex_year = j['publication_year']
	openalex_publication_date = j['publication_date']
	openalex_doi = j['doi']
	venue = j['host_venue']
	openalex_venue_id = venue['id']
	openalex_url = venue['url']
	openalex_venue_name = venue['display_name']
	openalex_publisher = venue['publisher']
	publication_type = j['type']
	openalex_first_page = j['biblio']['first_page']
	openalex_last_page = j['biblio']['last_page']
	# num_pages = (np.NaN if openalex_first_page is None or openalex_last_page is None 
	# 	else int(openalex_last_page) - int(openalex_first_page) + 1)
	num_references = len(j['referenced_works'])
	num_citations = j['cited_by_count']
	# cited_by_api_url is a little bit complicated because in the results of title query
	#   it returns a list whereas it returns a str in doi query
	cited_url = j['cited_by_api_url']
	cited_by_api_url = cited_url if type(cited_url) is str else cited_url[0]
	num_cited_by_api_url = 1 if type(cited_url) is str else len(cited_url)
	paper_dict = {
		'Reference': re.sub('//api.', '//', url),
		'OpenAlex Year': openalex_year,
		'OpenAlex Publication Date': openalex_publication_date,
		'OpenAlex ID': openalex_id,
		'OpenAlex Title': openalex_title,
		'OpenAlex DOI': openalex_doi,
		'OpenAlex URL': openalex_url,
		'OpenAlex Venue ID': openalex_venue_id,
		'OpenAlex Venue Name': openalex_venue_name,
		'OpenAlex Publisher': openalex_publisher,
		'Publication Type': publication_type,
		'OpenAlex First Page': openalex_first_page,
		'OpenAlex Last Page': openalex_last_page,
		# 'Number of Pages': num_pages,
		'Number of References for Reference paper': num_references,
		'Number of Citations': num_citations,
		'Number of Authors': num_authors,
		'Number of Concepts': num_concepts,
		'Citation API URL': cited_by_api_url,
		'Number of Citation API URLs': num_cited_by_api_url,
	}
	paper_dict_list.append(paper_dict)
	return paper_dict_list

def get_author_dict_list_from_authors(j, url, author_dict_list):
	"""returns a list of dicts
	"""
	openalex_id = re.sub('https://openalex.org/', '', j['id'])
	openalex_title = j['display_name']
	openalex_year = j['publication_year']
	authors = j['authorships']
	num_authors = len(authors)
	for i in authors:
		author = i['author']
		author_name = author['display_name']
		author_position = authors.index(i) + 1
		position_type = i['author_position']
		openalex_author_id = author['id']
		author_orcid = author['orcid']
		raw_affiliation_string = i['raw_affiliation_string']
		if len(i['institutions']) == 0:
			num_institutions = np.NaN
			first_institution = np.NaN
			institution_name = np.NaN
			institution_id = np.NaN
			ror = np.NaN
			country_code = np.NaN
			institution_type = np.NaN
		else:
			num_institutions = len(i['institutions'])
			first_institution = i['institutions'][0]
			institution_name = first_institution['display_name']
			institution_id = first_institution['id']
			ror = first_institution['ror']
			country_code = first_institution['country_code']
			institution_type = first_institution['type']
		author_dict = {
			'Reference': re.sub('//api.', '//', url),
			'Reference OpenAlex Year': openalex_year,
			'Reference OpenAlex ID': openalex_id,
			'Reference OpenAlex Title': openalex_title,
			'Number of Authors': num_authors,
			'Author Name': author_name,
			'Author Position': author_position,
			'Author Position Type': position_type,
			'OpenAlex Author ID': openalex_author_id,
			'Author ORCID': author_orcid,
			'Number of Affiliations': num_institutions,
			'First Institution Name': institution_name,
			'Raw Affiliation String': raw_affiliation_string,
			'First Institution ID': institution_id,
			'First Institution ROR': ror,
			'First Institution Type': institution_type,
			'First Institution Country Code': country_code
		}
		author_dict_list.append(author_dict)
	return author_dict_list

def get_concept_dict_list_from_concepts(j, url, concept_dict_list):
	"""returns a list of dicts
	"""
	openalex_id = re.sub('https://openalex.org/', '', j['id'])
	openalex_title = j['display_name']
	openalex_year = j['publication_year']
	concepts = j['concepts']
	num_concepts = len(concepts)
	for i in concepts:
		concept_index = concepts.index(i) + 1
		concept_name = i['display_name']
		openalex_concept_id = i['id']
		wikidata_url = i['wikidata']
		level = i['level']
		score = i['score']
		concept_dict = {
			'Reference': re.sub('//api.', '//', url),
			'Reference OpenAlex Year': openalex_year,
			'Reference OpenAlex ID': openalex_id,
			'Reference OpenAlex Title': openalex_title,
			'Number of Concepts': num_concepts,
			'Index of Concept': concept_index,
			'Concept': concept_name,
			'Concept ID': openalex_concept_id,
			'Wikidata': wikidata_url,
			'Level': level,
			'Score': score,
		}
		concept_dict_list.append(concept_dict)
	return concept_dict_list

def main(URLS, s, headers):
	for url in URLS:
		url_index = URLS.index(url) + 1
		api_url = re.sub('https://', 'https://api.', url)
		response = s.get(api_url, headers=headers)
		# if the response.status_code is in retry_code, then there is something wrong
		#    I will sleep for a while and try again. Note that if the status_code is 404, 
		#      I except it and put it in error_url_dict
		while response.status_code in retry_code:
			print(f'doi query {url_index} : {api_url} has error, status code is {response.status_code}, retrying...')
			time.sleep(3)
			response = s.get(api_url, headers=headers)
		# note that if the error code is 404, which means the following `response.jons()` will fail,
		#   then that url will NOT be included in paper_dict, author_dict, or concept list
		#.   Instead, that url will be put in error_url_dict
		#.     This is not a problem because later when I merge with REF, the merged file
		#.       will show NaN for 'number of concepts'....
		#.        In fact, even if I create empty dicts for those urls with 404 status codes,
		#          the final merged output will be the same. 
		try:
			j = response.json()
			get_paper_dict_from_json_result(j, url, paper_dict_list)
			get_author_dict_list_from_authors(j, url, author_dict_list)
			get_concept_dict_list_from_concepts(j, url, concept_dict_list)
			print(f'{url_index} / {len(URLS)} is done')
		except:
			error_url_dict = {
			    'Error URL': url,
			    'Error Status Code': response.status_code,
			}
			error_url_dict_list.append(error_url_dict)
			print(f'{url} : {response.status_code}')
		time.sleep(0.5)

if __name__ == '__main__':
	s = get_s()[0]
	headers = get_s()[1]
	# REF is openalex_reference_df with rows omitted whose 'number of reference' is missing
	REF = get_unique_ref_urls(OPENALEX_REFERENCE_DF)[0]
	URLS = get_unique_ref_urls(OPENALEX_REFERENCE_DF)[1]
	random_urls = URLS[0:11]
	paper_dict_list = []
	author_dict_list = []
	concept_dict_list = []
	error_url_dict_list = []
	retry_code = [ 500, 502, 503, 504, 429]
	main(URLS, s, headers)
	paper_df = pd.DataFrame(paper_dict_list)
	author_df = pd.DataFrame(author_dict_list)
	concept_df = pd.DataFrame(concept_dict_list)
	error_df = pd.DataFrame(error_url_dict_list)
	ref_paper_df = REF.merge(paper_df, on="Reference", how='left')
	ref_author_df = REF.merge(author_df, on="Reference", how='left')
	ref_concept_df = REF.merge(concept_df, on="Reference", how='left')
	paper_df.to_csv(OPENALEX_REFERENCE_PAPER_DF_UNIQUE, index=False)
	author_df.to_csv(OPENALEX_REFERENCE_AUTHOR_DF_UNIQUE, index=False)
	concept_df.to_csv(OPENALEX_REFERENCE_CONCEPT_DF_UNIQUE, index=False)
	ref_paper_df.to_csv(OPENALEX_REFERENCE_PAPER_DF, index=False)
	ref_author_df.to_csv(OPENALEX_REFERENCE_AUTHOR_DF, index=False)
	ref_concept_df.to_csv(OPENALEX_REFERENCE_CONCEPT_DF, index=False)
	error_df.to_csv(OPENALEX_REFERENCE_ERROR_DF, index=False)