""" this script generates dataframes for citation papers. 

input: openalex_paper_df

output: openalex_citation author_df, concept_df, and paper_df

"""

import pandas as pd 
import numpy as np 
import requests
import random
import math
import re 
import sys 
import time 
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import json 

OPENALEX_PAPER_DF = sys.argv[1]
OPENALEX_CITATION_AUTHOR_DF = sys.argv[2]
OPENALEX_CITATION_CONCEPT_DF = sys.argv[3]
OPENALEX_CITATION_PAPER_DF = sys.argv[4]

def get_dicts(OPENALEX_PAPER_DF): # vispd_openalex_match here is OPENALEX_PAPER_DF
	df = pd.read_csv(OPENALEX_PAPER_DF)
	dois = df['DOI'].tolist()
	urls = df['Citation API URL'].tolist()
	openalex_ids = df['OpenAlex ID'].tolist()
	years = df['Year'].tolist()
	titles = df['Title'].tolist()
	doi_year_dict = dict(zip(dois, years))
	doi_title_dict = dict(zip(dois, titles))
	doi_url_dict = dict(zip(dois, urls))
	doi_openalexID_dict = dict(zip(dois, openalex_ids))
	return [dois, urls, doi_year_dict, doi_title_dict, doi_url_dict, doi_openalexID_dict]

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

def get_concept_dict_list_from_concepts(doi, result, concepts):
	"""returns a list of dicts
	"""
	openalex_year = result['publication_year']
	openalex_id = re.sub('https://openalex.org/', '', result['id'])
	openalex_title = result['display_name']
	openalex_doi = result['doi']
	concept_dict_list = []
	num_concepts = len(concepts)
	for i in concepts:
		concept_index = concepts.index(i) + 1
		concept_name = i['display_name']
		openalex_concept_id = i['id']
		wikidata_url = i['wikidata']
		level = i['level']
		score = i['score']
		concept_dict = {
			'Cited Ppaer Year': doi_year_dict[doi],
			'Cited Paper DOI': doi,
			'Cited Paper Title': doi_title_dict[doi],
			'Cited Paper OpenAlex ID': doi_openalexID_dict[doi],
			'Citation Paper Year': openalex_year,
			'Citation Paper OpenAlex ID': openalex_id,
			'Citation Ppaer OpenAlex Title': openalex_title,
			'Citation Paper OpenAlex DOI': openalex_doi,
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

def get_author_dict_list_from_authors(doi, result, authors):
	"""returns a list of dicts
	"""
	openalex_year = result['publication_year']
	openalex_id = re.sub('https://openalex.org/', '', result['id'])
	openalex_title = result['display_name']
	openalex_doi = result['doi']
	author_dict_list = []
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
			# Check whether the institution object is empty
			# this is because, in the first citation of 10.1109/TVCG.2007.70599
			# the first author's institution is empty, which causes errors 
			if first_institution:
				institution_name = first_institution['display_name']
				institution_id = first_institution['id']
				ror = first_institution['ror']
				country_code = first_institution['country_code']
				institution_type = first_institution['type']
			else:
				institution_name = np.NaN
				institution_id = np.NaN
				ror = np.NaN
				country_code = np.NaN
				institution_type = np.NaN
		author_dict = {
			'Cited Ppaer Year': doi_year_dict[doi],
			'Cited Paper DOI': doi,
			'Cited Paper Title': doi_title_dict[doi],
			'Cited Paper OpenAlex ID': doi_openalexID_dict[doi],
			'Citation Paper Year': openalex_year,
			'Citation Paper OpenAlex ID': openalex_id,
			'Citation Ppaer OpenAlex Title': openalex_title,
			'Citation Paper OpenAlex DOI': openalex_doi,
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

def get_paper_dict_from_json_result(j, doi):
	"""returns a dict 
	"""
	authors = j['authorships']
	num_authors = len(authors)
	concepts = j['concepts']
	num_concepts = len(concepts)
	openalex_year = j['publication_year']
	openalex_id = re.sub('https://openalex.org/', '', j['id'])
	openalex_title = j['display_name']
	openalex_doi = j['doi']
	openalex_publication_date = j['publication_date']
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
		'Cited Ppaer Year': doi_year_dict[doi],
		'Cited Paper DOI': doi,
		'Cited Paper Title': doi_title_dict[doi],
		'Cited Paper OpenAlex ID': doi_openalexID_dict[doi],
		'OpenAlex Year': openalex_year,
		'OpenAlex Publication Date': openalex_publication_date,
		'Citation Paper OpenAlex ID': openalex_id,
		'Citation Paper OpenAlex Title': openalex_title,
		'Citation Paper OpenAlex DOI': openalex_doi,
		'Citation Paper OpenAlex URL': openalex_url,
		'OpenAlex Venue ID': openalex_venue_id,
		'OpenAlex Venue Name': openalex_venue_name,
		'OpenAlex Publisher': openalex_publisher,
		'Publication Type': publication_type,
		'OpenAlex First Page': openalex_first_page,
		'OpenAlex Last Page': openalex_last_page,
		# 'Number of Pages': num_pages,
		'Number of References': num_references,
		'Number of Authors': num_authors,
		'Number of Concepts': num_concepts,
		'Number of Citations': num_citations,
		'Citation API URL': cited_by_api_url,
		'Number of Citation API URLs': num_cited_by_api_url,
	}
	return paper_dict

def get_empty_dict_list(doi):
	dict_list = [{
		'Cited Ppaer Year': doi_year_dict[doi],
		'Cited Paper DOI': doi,
		'Cited Paper Title': doi_title_dict[doi],
		'Cited Paper OpenAlex ID': doi_openalexID_dict[doi],
	}]
	return dict_list

def get_empty_dict(doi):
	a_dict = {
		'Cited Ppaer Year': doi_year_dict[doi],
		'Cited Paper DOI': doi,
		'Cited Paper Title': doi_title_dict[doi],
		'Cited Paper OpenAlex ID': doi_openalexID_dict[doi],
	}
	return a_dict 

def get_json_result(url, s, headers):
	"""if 404 or other error codes, retry
	This function prevents error codes. I am pretty sure that every api_cited_url will get 
		a status_code of 200, that's why I am confident to use this function

	Also, it should be noted that if the status code is 404, then s.get(url).json() will 
		throw an error. So i don't need to check the status code in this function. 
	"""
	try: 
		j = s.get(url, headers=headers).json()
	except:
		time.sleep(1) 
		return get_json_result(url, s, headers)
	else:
		return j

def main(DOIS, s, headers):
	for doi in DOIS:
		# to make sure the api-url is not nan:
		if doi_url_dict[doi] == doi_url_dict[doi]:
			url = doi_url_dict[doi] + '&per-page=50'
			j0 = get_json_result(url, s, headers)
			count = j0['meta']['count']
			per_page = 50
			total_pages = math.ceil(count/per_page)
			# checking whether results are empty
			if count > 0:
				# for every page
				for i in range(1,total_pages+1):
					list_of_concept_dict_lists = []
					list_of_author_dict_lists = []
					paper_dict_list = []
					j = get_json_result(url + f'&page={i}', s, headers=headers)
					results = j['results']
					# for every result in a page
					for result in results:
						concepts = result['concepts']
						authors = result['authorships']
						concept_dict_list = get_concept_dict_list_from_concepts(doi, result, concepts)
						author_dict_list = get_author_dict_list_from_authors(doi, result, authors)
						paper_dict = get_paper_dict_from_json_result(result, doi)
						list_of_concept_dict_lists.append(concept_dict_list)
						list_of_author_dict_lists.append(author_dict_list)
						paper_dict_list.append(paper_dict)
					lists_concepts.append(list_of_concept_dict_lists)
					lists_authors.append(list_of_author_dict_lists)
					list_of_paper_dict_lists.append(paper_dict_list)
					time.sleep(0.2)

			# if empty results:
			else:
				list_of_concept_dict_lists = []
				list_of_author_dict_lists = []
				paper_dict_list = []
				concept_dict_list = get_empty_dict_list(doi)
				author_dict_list = get_empty_dict_list(doi)
				paper_dict = get_empty_dict(doi)
				list_of_concept_dict_lists.append(concept_dict_list)
				list_of_author_dict_lists.append(author_dict_list)
				paper_dict_list.append(paper_dict)
				lists_concepts.append(list_of_concept_dict_lists)
				lists_authors.append(list_of_author_dict_lists)
				list_of_paper_dict_lists.append(paper_dict_list)
		else:
			list_of_concept_dict_lists = []
			list_of_author_dict_lists = []
			paper_dict_list = []
			concept_dict_list = get_empty_dict_list(doi)
			author_dict_list = get_empty_dict_list(doi)
			paper_dict = get_empty_dict(doi)
			list_of_concept_dict_lists.append(concept_dict_list)
			list_of_author_dict_lists.append(author_dict_list)
			paper_dict_list.append(paper_dict)
			lists_concepts.append(list_of_concept_dict_lists)
			lists_authors.append(list_of_author_dict_lists)
			list_of_paper_dict_lists.append(paper_dict_list)
		print(f'{DOIS.index(doi) + 1} is done')
		time.sleep(0.5)

if __name__ == '__main__':
	# I don't need to worry papers having no citations. 
	# This is because even if there is no citation, there is still a cited_api_url
	# and the result count in that cited_api_url will be zero.
	# I have solved this issue in main()
	dois = get_dicts(OPENALEX_PAPER_DF)[0]
	random_dois = random.sample(dois, 10)
	urls = get_dicts(OPENALEX_PAPER_DF)[1]
	doi_year_dict = get_dicts(OPENALEX_PAPER_DF)[2]
	doi_title_dict = get_dicts(OPENALEX_PAPER_DF)[3]
	doi_url_dict = get_dicts(OPENALEX_PAPER_DF)[4]
	doi_openalexID_dict = get_dicts(OPENALEX_PAPER_DF)[5]
	lists_concepts = [] # list of lists of concept dict lists
	lists_authors = [] # list of lists of author dict lists
	list_of_paper_dict_lists = [] # list of paper dict lists
	s = get_s()[0]
	headers = get_s()[1]
	main(dois, s, headers)
	
author_df_initiate = pd.DataFrame()
concept_df_initiate = pd.DataFrame()

def build_df_from_lists(lists, df):
	for i in lists:
		df1 = pd.concat([pd.DataFrame(l) for l in i], ignore_index=True)
		df = df.append(df1, ignore_index=True)
	return df 

author_df = build_df_from_lists(lists_authors, author_df_initiate)
concept_df = build_df_from_lists(lists_concepts, concept_df_initiate)
paper_df = pd.concat(
	[pd.DataFrame(l) for l in list_of_paper_dict_lists], ignore_index=True)

author_df.to_csv(OPENALEX_CITATION_AUTHOR_DF, index=False)
concept_df.to_csv(OPENALEX_CITATION_CONCEPT_DF, index=False)
paper_df.to_csv(OPENALEX_CITATION_PAPER_DF, index=False)

# 146 Citation papers are simply empty data. I need to exclude them before writing to files
# author_df[author_df['Citation Paper OpenAlex ID'].notnull()].to_csv(
# 	OPENALEX_CITATION_AUTHOR_DF, index=False)
# concept_df[concept_df['Citation Paper OpenAlex ID'].notnull()].to_csv(
# 	OPENALEX_CITATION_CONCEPT_DF, index=False)
# paper_df[paper_df['Citation Paper OpenAlex ID'].notnull()].to_csv(
# 	OPENALEX_CITATION_PAPER_DF, index=False)

