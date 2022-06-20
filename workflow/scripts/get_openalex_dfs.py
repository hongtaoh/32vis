""" This script generates dataframes for papers_to_study

input: papers_to_study, vispubdata_plus

output: openalex paper_df, author_df, concept_df, 
		reference_df, title_query_empty_doi_query_404, title_query_404, and doi_query_404

"""
import pandas as pd 
import numpy as np 
import requests
import random
import math
import csv  
import re 
import sys 
import time 
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

PAPERS_TO_STUDY = sys.argv[1]
VISPUBDATA_PLUS = sys.argv[2]
OPENALEX_PAPER_DF = sys.argv[3]
OPENALEX_AUTHOR_DF = sys.argv[4]
OPENALEX_CONCEPT_DF = sys.argv[5]
OPENALEX_REFERENCE_DF = sys.argv[6]
TITEL_QUERY_EMPTY_DOI_QUERY_404_DFS = sys.argv[7]
TITLE_QUERY_404_DFS = sys.argv[8]
DOI_QUERY_404_DFS = sys.argv[9]

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

def get_concept_dict_list_from_concepts(doi, concepts):
	"""returns a list of dicts
	"""
	concept_dict_list = []
	num_concepts = len(concepts)
	# first check whether the list concepts is empty:
	if concepts:
		for i in concepts:
			concept_index = concepts.index(i) + 1
			concept_name = i['display_name']
			openalex_concept_id = i['id']
			wikidata_url = i['wikidata']
			level = i['level']
			score = i['score']
			concept_dict = {
				'Year': doi_year_dict[doi],
				'DOI': doi,
				'Title': doi_title_dict[doi],
				'Number of Concepts': num_concepts,
				'Index of Concept': concept_index,
				'Concept': concept_name,
				'Concept ID': openalex_concept_id,
				'Wikidata': wikidata_url,
				'Level': level,
				'Score': score,
			}
			concept_dict_list.append(concept_dict)
	# if concept list is empty, 'number of concepts' will be NaN
	else:
		concept_dict = {
			'Year': doi_year_dict[doi],
			'DOI': doi,
			'Title': doi_title_dict[doi],
		}
		concept_dict_list.append(concept_dict)
	return concept_dict_list

def get_reference_dict_list_from_referenced_works(doi, referenced_works):
	reference_dict_list = []
	num_references = len(referenced_works)
	# first check whether the list of referenced works is empty
	if referenced_works:
		for i in referenced_works:
			reference_index = referenced_works.index(i) + 1
			reference_dict = {
				'Year': doi_year_dict[doi],
				'DOI': doi,
				'Title': doi_title_dict[doi],
				'Number of References': num_references,
				'Index of Reference': reference_index,
				'Reference': i,
			}
			reference_dict_list.append(reference_dict)
	# if refs list is empty, 'number of references' will be NaN
	else:
		reference_dict = {
			'Year': doi_year_dict[doi],
			'DOI': doi,
			'Title': doi_title_dict[doi],
		}
		reference_dict_list.append(reference_dict)
	return reference_dict_list

def get_author_dict_list_from_authors(doi, authors):
	"""returns a list of dicts
	"""
	author_dict_list = []
	num_authors = len(authors)
	# first check whether authors is empty
	if authors:
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
				'Year': doi_year_dict[doi],
				'DOI': doi,
				'Title': doi_title_dict[doi],
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
	# if authors list is empty, 'number of authors' will be NaN
	else:
		author_dict = {
			'Year': doi_year_dict[doi],
			'DOI': doi,
			'Title': doi_title_dict[doi],
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
	num_pages = (np.NaN if openalex_first_page is None or openalex_last_page is None 
		else int(openalex_last_page) - int(openalex_first_page) + 1)
	num_references = len(j['referenced_works'])
	num_citations = j['cited_by_count']
	# cited_by_api_url is a little bit complicated because in the results of title query
	#   it returns a list whereas it returns a str in doi query
	cited_url = j['cited_by_api_url']
	cited_by_api_url = cited_url if type(cited_url) is str else cited_url[0]
	num_cited_by_api_url = 1 if type(cited_url) is str else len(cited_url)
	paper_dict = {
		'Year': doi_year_dict[doi],
		'DOI': doi,
		'Title': doi_title_dict[doi],
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
		'Number of Pages': num_pages,
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
		'Year': doi_year_dict[doi],
		'DOI': doi,
		'Title': doi_title_dict[doi],
	}]
	return dict_list

def get_empty_paper_dict(doi):
	paper_dict = {
		'Year': doi_year_dict[doi],
		'DOI': doi,
		'Title': doi_title_dict[doi],
	}
	return paper_dict

def get_title_query_response(doi):
	title = doi_title_dict[doi]
	title_to_query = re.sub(r'\:|\?|\&|\,', '', title)
	response = requests.get(
		'https://api.openalex.org/works?filter=title.search:' + title_to_query)
	return response, title_to_query

def check_results_count(response):
	j = response.json()
	count = j['meta']['count']
	return j, count 

def get_doi_query_response(doi):
	response = requests.get("https://api.openalex.org/works/doi:" + doi)
	return response

def get_data(doi, doi_index):
	# if doi not in to_query_by_doi, query title first
	if doi not in to_query_by_doi:
		# query title first:
		response = get_title_query_response(doi)[0]
		# if the response.status_code is in retry_code, then there is something wrong
		#    I will sleep for a while and try again. Note that if the status_code is 404, 
		#      I put it to no_matching (see below, if status_code != 200), rather than retryihng
		while response.status_code in retry_code:
			print(f'Title query has errors for {doi_index} : {doi_title_dict[doi]}. Error status code is {response.status_code}. Retrying...')
			time.sleep(3)
			response = get_title_query_response(doi)[0]
		# if title query succeeds:
		if response.status_code == 200:
			# get json and check results count:
			j = check_results_count(response)[0]
			count = check_results_count(response)[1]
			# if count is non-zero:
			if count > 0:
				# if doi not in special_result_index_dict, use index of 0
				#   otherwise, use the value corresponding to the key
				if doi not in list(special_result_index_dict.keys()):
					correct_result = j['results'][0]
				else:
					correct_index = special_result_index_dict[doi]
					correct_result = j['results'][correct_index]
				authors = correct_result['authorships']
				concepts = correct_result['concepts']
				referenced_works = correct_result['referenced_works']
				paper_dict = get_paper_dict_from_json_result(correct_result, doi)
				author_dict_list = get_author_dict_list_from_authors(doi, authors)
				concept_dict_list = get_concept_dict_list_from_concepts(doi, concepts)
				reference_dict_list = get_reference_dict_list_from_referenced_works(doi, referenced_works)
			# if count is zero, query doi instead
			else:
				# get doi query response:
				response2 = get_doi_query_response(doi)
				# if status code is in retry_code, retry
				while response2.status_code in retry_code:
					print(f'doi query has error for {doi_index} : {doi}, error status code is {response2.status_code}, retrying...')
					time.sleep(3)
					response2 = get_doi_query_response(doi)
				# if doi query succeeds:
				if response2.status_code == 200:
					j2 = response2.json()
					authors = j2['authorships']
					concepts = j2['concepts']
					referenced_works = j2['referenced_works']
					paper_dict = get_paper_dict_from_json_result(j2, doi)
					author_dict_list = get_author_dict_list_from_authors(doi, authors)
					concept_dict_list = get_concept_dict_list_from_concepts(doi, concepts)
					reference_dict_list = get_reference_dict_list_from_referenced_works(doi, referenced_works)
				# if doi query fails, add the doi to no_result_bad_doi list
				else:
					error_status_code(response2.status_code)
					title_query_empty_doi_query_404_list.append(doi)
					paper_dict = get_empty_paper_dict(doi)
					author_dict_list = get_empty_dict_list(doi)
					concept_dict_list = get_empty_dict_list(doi)
					reference_dict_list = get_empty_dict_list(doi)
					print(f'doi query fails for {doi_index} : {doi}')
		# if title query fails (most likely status code 404), which is very unlikely!
		#    add it to no_title_matching
		else:
			title_query_404_list.append(doi)
			error_status_code.append(response.status_code)
			paper_dict = get_empty_paper_dict(doi)
			author_dict_list = get_empty_dict_list(doi)
			concept_dict_list = get_empty_dict_list(doi)
			reference_dict_list = get_empty_dict_list(doi)
			print(f'title query fails for {doi_index} : {doi_title_dict[doi]}')
	# if doi in to_query_by_doi, use doi query
	else:
		# get doi query response:
		response0 = get_doi_query_response(doi)
		# if status code is in retry_code, retry
		while response0.status_code in retry_code:
			print(f'doi query for {doi_index} : {doi} has error, status code is {response0.status_code}, retrying...')
			time.sleep(3)
			response0 = get_doi_query_response(doi)
		# if doi query succeeds:
		if response0.status_code == 200:
			j0 = response0.json()
			authors = j0['authorships']
			concepts = j0['concepts']
			referenced_works = j0['referenced_works']
			paper_dict = get_paper_dict_from_json_result(j0, doi)
			author_dict_list = get_author_dict_list_from_authors(doi, authors)
			concept_dict_list = get_concept_dict_list_from_concepts(doi, concepts)
			reference_dict_list = get_reference_dict_list_from_referenced_works(doi, referenced_works)
		# if doi query fails, add the doi to no_doi_matching
		else:
			error_status_code.append(response0.status_code)
			doi_query_404_list.append(doi)
			paper_dict = get_empty_paper_dict(doi)
			author_dict_list = get_empty_dict_list(doi)
			concept_dict_list = get_empty_dict_list(doi)
			reference_dict_list = get_empty_dict_list(doi)
			print(f'doi query fails for {doi_index} : {doi}')
	list_of_paper_dicts.append(paper_dict)
	list_of_author_dict_lists.append(author_dict_list)
	list_of_concept_dict_lists.append(concept_dict_list)
	list_of_reference_dict_lists.append(reference_dict_list)

def main(DOIS):
	for doi in DOIS:
		doi_index = DOIS.index(doi) + 1
		get_data(doi, doi_index)
		print(f'{doi_index} is done')
		time.sleep(0.5)
	print(list(set(error_status_code)))

if __name__ == '__main__':
	papers_to_study = read_txt(PAPERS_TO_STUDY)
	random_papers_to_study = random.sample(papers_to_study, 10)
	doi_year_dict = get_dicts(VISPUBDATA_PLUS)[0]
	doi_title_dict = get_dicts(VISPUBDATA_PLUS)[1]
	list_of_paper_dicts = []
	list_of_author_dict_lists = []
	list_of_concept_dict_lists = []
	list_of_reference_dict_lists = []
	title_query_empty_doi_query_404_list = []
	title_query_404_list = []
	doi_query_404_list = []
	retry_code = [ 500, 502, 503, 504, 429]
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
	main(papers_to_study)
	
paper_df = pd.DataFrame(list_of_paper_dicts)
author_df = pd.concat(
	[pd.DataFrame(l) for l in list_of_author_dict_lists], ignore_index=True)
concept_df = pd.concat(
	[pd.DataFrame(l) for l in list_of_concept_dict_lists], ignore_index=True)
reference_df = pd.concat(
	[pd.DataFrame(l) for l in list_of_reference_dict_lists], ignore_index=True)

paper_df.to_csv(OPENALEX_PAPER_DF, index=False)
author_df.to_csv(OPENALEX_AUTHOR_DF, index=False)
concept_df.to_csv(OPENALEX_CONCEPT_DF, index=False)
reference_df.to_csv(OPENALEX_REFERENCE_DF, index=False)

with open(TITEL_QUERY_EMPTY_DOI_QUERY_404_DFS, 'w') as f:
	for doi in title_query_empty_doi_query_404_list:
		f.write("%s\n" % doi)

with open(TITLE_QUERY_404_DFS, 'w') as f:
	for doi in title_query_404_list:
		f.write("%s\n" % doi)

with open(DOI_QUERY_404_DFS, 'w') as f:
	for doi in doi_query_404_list:
		f.write("%s\n" % doi)