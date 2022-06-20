"""scrape IEEE VIS 2021 and obtain the list of paper titles

output: processed/titles_2021.csv

"""

import sys
import pandas as pd
import requests
from bs4 import BeautifulSoup

TITLES_2021 = sys.argv[1]

def get_page(url):
	r = requests.get(url)
	soup = BeautifulSoup(r.content, 'lxml')
	page = soup.find('article')
	return page

page = get_page('http://ieeevis.org/year/2021/info/papers-sessions')

def get_all_title_str(page):
	"""all_title_str contains both full and short papers' titles
	"""
	strong_elements = page.find_all('strong')
	time_str_elements = [
		x for x in strong_elements if 'CDT' in x.string or 'October' in x.string
	]
	all_title_str = [x.string for x in strong_elements if x not in time_str_elements]
	return all_title_str

all_title_str = get_all_title_str(page)

def get_str_to_exclude(page):
	"""i obtain the list of short paper titles

	First, I obtain both 'strong' and 'em'. Then, I obtain the index of the line that contain 'short papers:'
	That will serve as the "starting index" later. 

	Then, for each line that contain 'short papers:', i obtain the index of the immediate line that contains
	'session chair:'. That index will serve as the "end index".

	For each "starting" and "end" pair, I got the elements in between an extract their string. These include 
	all short papers' titlees. 

	"""
	strong_and_em = page.find_all(['strong', 'em'])
	short_paper_em_idx = [
		strong_and_em.index(i) for i in strong_and_em if 'Short Papers:' in i.string
	]
	session_chair_em_idx = [
		strong_and_em.index(i) for i in strong_and_em if 'Session Chair:' in i.string
	]
	end_idx_list = []
	for idx in short_paper_em_idx:
		end_idx = session_chair_em_idx.index(idx+1)
		end_idx_list.append(session_chair_em_idx[end_idx+1])
	start_end_dic = dict(zip(short_paper_em_idx, end_idx_list))
	str_to_exclude_list = []
	for start in start_end_dic.keys():
		to_exclude = strong_and_em[start:start_end_dic[start]]
		str_to_exclude = [x.string for x in to_exclude]
		str_to_exclude_list.append(str_to_exclude)
	str_to_exclude_list_flattened = [
		item for sublist in str_to_exclude_list for item in sublist
	]
	return str_to_exclude_list_flattened

str_to_exclude = get_str_to_exclude(page)

title_str = [x for x in all_title_str if x not in str_to_exclude]

title_str.remove(
	'Jurassic Mark: Inattentional Blindness for a Datasaurus Reveals that Visualizations are Explored, not Seen'
)

# This paper changed its title for publication on TCVG
title_replace_dict = {
    'IRVINE: Using Interactive Clustering and Labeling to Analyze Correlation Patterns: A Design Study from the Manufacturing of Electrical Engines':
    'IRVINE: A Design Study on Analyzing Correlation Patterns of Electrical Engines',
}

def replace_title(TITLES, DIC):
    for i,n in enumerate(TITLES):
        if n in DIC.keys():
            TITLES[i] = DIC[n]
    return TITLES

title_str = replace_title(title_str, title_replace_dict)

if len(title_str) == 170:
	print('title_str has 170 elements. everything correct')
else:
	print('something is wrong. the length of title_str is not 170')

df = pd.DataFrame(title_str, columns=['title'])

df.to_csv(TITLES_2021, index=False)