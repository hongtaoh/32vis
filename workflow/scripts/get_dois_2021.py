"""get the dois of 2021 IEEE VIS papers, and vispubdata_plus

input: titles_2021, vispubdata

output: dois_2021, vispubdata_plus

"""

import sys
from habanero import Crossref
import pandas as pd

TITLES_2021 = sys.argv[1]
VISPUBDATA = sys.argv[2]
DOIS_2021 = sys.argv[3]
VISPUBDATA_PLUST = sys.argv[4]

def get_query_titles(TITLES_2021):
	df = pd.read_csv(TITLES_2021)
	titles = df.title.tolist()
	return titles 

def get_title_doi_dict_list(titles, t):
	"""this function querys the CrossRef API using titles 
	"""
	try: 
		x = cr.works(query=t)
		first_item = x['message']['items'][0]
		cr_title = first_item['title'][0]
		cr_doi = first_item['DOI']
		cr_year = first_item['indexed']['date-parts'][0][0]
		title_doi_dict = {
			'title': t,
			'crossref title': cr_title,
			'crossref doi': cr_doi,
			'crossref year': cr_year,
		}
		title_doi_dict_list.append(title_doi_dict)
		print(f'{titles.index(t) + 1} is done')
	except:
		print(f'{titles.index(t) + 1} has something wrong')

# The following titles had wrong query results.
# I manually collected their DOI information from IEEE Xplore
manual_title_doi_dict = {
	'Interactive Dimensionality Reduction for Comparative Analysis': '10.1109/TVCG.2021.3114807',
    'Real-Time Denoising of Volumetric Path Tracing for Direct Volume Rendering': '10.1109/TVCG.2020.3037680',
    '3D Virtual Pancreatography': '10.1109/TVCG.2020.3020958',
    'Rethinking the Ranks of Visual Channels': '10.1109/TVCG.2021.3114684',
    'Modeling Just Noticeable Differences in Charts': '10.1109/TVCG.2021.3114874',
    'What we talk about when we talk about data physicality': '10.1109/MCG.2020.3024146',
    'Natural Language to Visualization by Neural Machine Translation': '10.1109/TVCG.2021.3114848',
    'Gosling: A Grammar-based Toolkit for Scalable and Interactive Genomics Data Visualization': '10.1109/TVCG.2021.3114876',
    'Interactive Graph Construction for Graph-Based Semi-Supervised Learning': '10.1109/TVCG.2021.3084694',
    'Differentiable Direct Volume Rendering': '10.1109/TVCG.2021.3114769',
    'Interactive Visual Exploration of Longitudinal Historical Career Mobility Data': '10.1109/TVCG.2021.3067200',
    'A State-of-the-Art Survey of Tasks for Tree Design and Evaluation with a Curated Task Dataset': '10.1109/TVCG.2021.3064037',
    'STRATISFIMAL LAYOUT: A Modular Optimization Model for Laying Out Layered Node-link Network Visualizations': '10.1109/TVCG.2021.3114756',
    'A Design Space for Applying the Freytag’s Pyramid Structure to Data Stories': '10.1109/TVCG.2021.3114774',
    'Interactive Data Comics': '10.1109/TVCG.2021.3114849',
    'Examining Effort in 1D Uncertainty Communication Using Individual Differences in Working Memory and NASA-TLX': '10.1109/TVCG.2021.3114803',
    'Visualization Equilibrium': '10.1109/TVCG.2021.3114842',
    'Visual Analysis of Hyperproperties for Understanding Model Checking Results': '10.1109/TVCG.2021.3114866',
    'COVID-view: Diagnosis of COVID-19 using Chest CT': '10.1109/TVCG.2021.3114851',
    'ThreadStates: State-based Visual Analysis of Disease Progression': '10.1109/TVCG.2021.3114840',
    'Loon: Using Exemplars to Visualize Large Scale Microscopy Data': '10.1109/TVCG.2021.3114766',
    'Scalable Scalable Vector Graphics: Automatic Translation of Interactive SVGs to a Multithread VDOM for Fast Rendering': '10.1109/TVCG.2021.3059294',
    'Probabilistic Data-Driven Sampling via Multi-Criteria Importance Analysis': '10.1109/TVCG.2020.3006426',
}

mismatch_title_doi_dict = {
	'Visual Evaluation for Autonomous Driving': '10.1109/TVCG.2021.3114777',
	'Visual Cascade Analytics of Large-scale Spatiotemporal Data': '10.1109/TVCG.2021.3071387',
	'Understanding Missing Links in Bipartite Networks with MissBiN': '10.1109/TVCG.2020.3032984',
	'Understanding Data Visualization Design Practice': '10.1109/TVCG.2021.3114959',
}

def get_dois_2021_df(title_doi_dict_list, manual_title_doi_dict, mismatch_title_doi_dict):
	"""combine the correct results with manual results
	"""
	title_doi_df = pd.DataFrame(title_doi_dict_list)
	cr_failed_titles_df = title_doi_df[~title_doi_df['crossref doi'].str.contains('10.1109')]
	cr_failed_titles = cr_failed_titles_df.title.tolist()
	if list(manual_title_doi_dict.keys()) == cr_failed_titles:
		print('I have covered all crossref failed titles!')
	else:
		print('ERROR! Some failed titles are not covered in the manual list!!!!!')
	manual_title_doi_dict = dict(
		list(manual_title_doi_dict.items()) + list(mismatch_title_doi_dict.items()))
	manual_titles = list(manual_title_doi_dict.keys())
	all_titles = title_doi_df.title.tolist()
	all_dois = title_doi_df['crossref doi'].tolist()
	all_dict = dict(zip(all_titles, all_dois))
	cr_success_titles = [x for x in all_titles if x not in manual_titles]
	cr_success_dois = [all_dict[x] for x in cr_success_titles]
	titles = cr_success_titles + manual_titles
	dois = cr_success_dois + list(manual_title_doi_dict.values())
	if len(dois) == 170:
		print('there are 170 dois. everything correct.')
	else:
		print('something is wrong with the total number of dois')
	df = pd.DataFrame ({
		'Conference': "VIS",
		'Year': 2021,
		'Title': titles,
		'DOI': dois,
	})
	return df 

def main(titles):
	for t in titles:
		get_title_doi_dict_list(titles, t)
	dois_2021_df = get_dois_2021_df(
		title_doi_dict_list, 
		manual_title_doi_dict,
		mismatch_title_doi_dict
	)
	return dois_2021_df

if __name__ == '__main__':
	titles = get_query_titles(TITLES_2021)
	cr = Crossref()
	title_doi_dict_list = []
	dois_2021_df = main(titles)
	vispd = pd.read_csv(VISPUBDATA)
	vispd_plus = vispd.append(dois_2021_df, ignore_index=True)
	dois_2021_df.to_csv(DOIS_2021, index=False)
	vispd_plus.to_csv(VISPUBDATA_PLUST, index=False)
