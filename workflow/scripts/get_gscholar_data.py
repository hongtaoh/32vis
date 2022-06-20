import sys
import pandas as pd
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC 
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException 
from selenium.common.exceptions import ElementNotInteractableException
import os
import random
import re
import csv
import numpy as np
import urllib.parse

PAPERS_TO_SUTDY = sys.argv[1]
IEEE_PAPER_DF = sys.argv[2]
GSCHOLAR_DATA = sys.argv[3]

def specify_driver_options():
	"""
	specify driver options
	"""
	options = Options()
	options.set_preference("browser.download.folderList", 2)
	options.set_preference("browser.download.manager.showWhenStarting", 
						   False)
	options.set_preference("browser.helperApps.neverAsk.saveToDisk", 
						   "text/plain, text/txt, application/plain, application/txt")

def read_txt(INPUT):
	"""read txt files and return a list
	"""
	raw = open(INPUT, "r")
	reader = csv.reader(raw)
	allRows = [row for row in reader]
	data = [i[0] for i in allRows]
	return data

def get_dicts(INPUT): # INPUT here is ieee_paper_df
	# get year_dict and title_dict
	df = pd.read_csv(INPUT)
	dois = df.loc[:, "DOI"].tolist()
	titles = df.loc[:, "IEEE Title"].tolist()
	years = df.loc[:, "Year"].tolist()
	doi_year_dict = dict(zip(dois, years))
	doi_title_dict = dict(zip(dois, titles))
	return doi_year_dict, doi_title_dict

def get_gscholar_data_by_title(doi, doi_index):
	# TITLE QUERY
	if doi in title_recode_dict.keys():
		title = title_recode_dict[doi]
	else:
		title = doi_title_dict[doi]
	title_to_query = urllib.parse.quote_plus(title)
	doi_to_query = urllib.parse.quote_plus(doi)
	query_string = 'https://scholar.google.com/scholar?hl=en&as_sdt=0%2C50&q='
	# IF DOI IN TO_QUERY_BY_DOI, USE DOI QUERY
	if doi in to_query_by_doi:
		driver.get(query_string + doi_to_query + '&btnG=')
		gs_paper_e = wait.until(EC.presence_of_element_located((
			By.CSS_SELECTOR, 'h3.gs_rt > a')))
	# IF NOT, USE TITLE QUERY
	else:
		driver.get(query_string + title_to_query + '&btnG=')
		try:
			gs_paper_e = wait.until(EC.presence_of_element_located((
				By.CSS_SELECTOR, 'h3.gs_rt > a')))
		# IF TITLE QUERY RESULT IS A [CITATION] PAPER, USE DOI QUERY INSTEAD
		except (NoSuchElementException, TimeoutException):
			# for example, 10.1109/INFVIS.2001.963279 will cause errors
			print(f'{doi_index} : {doi} has something wrong with title query. Its title is {title}. Trying doi query now')
			driver.get(query_string + doi_to_query + '&btnG=')
			gs_paper_e = wait.until(EC.presence_of_element_located((
				By.CSS_SELECTOR, 'h3.gs_rt > a')))
	gs_paper_title = gs_paper_e.text
	gs_paper_link = gs_paper_e.get_attribute('href')
	gs_citation_e = wait.until(
		EC.presence_of_element_located((By.XPATH, '//div[@class="gs_fl"]//child::a[3]'
	)))
	citation_link = gs_citation_e.get_attribute('href')
	citation_count_string = gs_citation_e.get_attribute('innerHTML')
	if citation_count_string == "Related articles":
		gs_citation_count = 0
	else:
		gs_citation_count = int(re.findall(r'\d+', citation_count_string)[0])	
	gscholar_dict = {
		'Year': doi_year_dict[doi],
		'DOI': doi,
		'IEEE Title': title,
		'Title on Google Scholar': gs_paper_title,
		'Paper Link': gs_paper_link,
		'Citation Link': citation_link,
		'Citation Counts on Google Scholar': gs_citation_count,
	}
	gscholar_dict_list.append(gscholar_dict)

def main(DOIS):
	for doi in DOIS:
		doi_index = DOIS.index(doi) + 1
		if doi != '10.1109/VISUAL.1991.175773':
			get_gscholar_data_by_title(doi, doi_index)
		else:
			'''as of June 19 2022, this paper is a [citation] paper
			'''
			gscholar_dict = {
				'Year': doi_year_dict[doi],
				'DOI': doi,
				'IEEE Title': doi_title_dict[doi],
				'Title on Google Scholar': 'A tool for visualizing the topology of three-dimensional vector fields',
				'Paper Link': np.NaN,
				'Citation Link': 'https://scholar.google.com/scholar?cites=17437623302222250489&as_sdt=5,50&sciodt=0,50&hl=en',
				'Citation Counts on Google Scholar': 371,
			}
			gscholar_dict_list.append(gscholar_dict)			
		print(f'{doi_index} is done')
		time.sleep(0.2+random.uniform(0, 0.2)) 
	driver.close()
	driver.quit()

if __name__ == '__main__':
	driver = webdriver.Firefox(options=specify_driver_options())
	wait = WebDriverWait(driver, 90)
	DOIS = read_txt(PAPERS_TO_SUTDY)
	doi_year_dict, doi_title_dict = get_dicts(IEEE_PAPER_DF)
	random_dois = random.sample(DOIS, 10)
	random_dois.append('10.1109/INFVIS.2001.963279')
	gscholar_dict_list = []
	title_recode_dict = {
	# If I don't change the title for querying, the results are wrong:
		'10.1109/INFVIS.2001.963279': 'Animated exploration of graphs with radial layout',
		'10.1109/INFVIS.2001.963295': 'Graphic Data Display for Cardiovascular System Case Study',
		'10.1109/VIS.1999.10000': 'Progressive compression of arbitrary triangular meshes',
		# This is the real title on PDF:
		'10.1109/VISUAL.1999.809889': 'Enabling classification and shading for 3 D texture mapping based volume rendering using OpenGL and extensions',

	}
	to_query_by_doi = [
	# If I query by title, the results are false:
		'10.1109/VISUAL.1993.398863',
		'10.1109/VISUAL.1996.567807',
		'10.1109/VISUAL.1998.745315',
		'10.1109/INFVIS.2001.963282',
		'10.1109/VISUAL.1992.235194',
		'10.1109/VISUAL.1993.398866',
		'10.1109/VISUAL.1998.745348',
		'10.1109/VISUAL.1997.663925',
		'10.1109/VISUAL.1993.398900',
		'10.1109/VISUAL.2000.885719',
		'10.1109/TVCG.2021.3114849',
		'10.1109/VISUAL.1991.175771',
		'10.1109/TVCG.2014.2346442',
	]
	main(DOIS)
	df = pd.DataFrame(gscholar_dict_list)
	df.to_csv(GSCHOLAR_DATA, index = False)