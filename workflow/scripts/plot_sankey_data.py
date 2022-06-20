"""This script prepares data for sankey diagrams on observablehq"""
import pandas as pd 
import sys
import numpy as np
import itertools
from collections import Counter

VISPUBDATA_PLUS = sys.argv[1]
OPENALEX_CONCEPT_DF = sys.argv[2]
REFERENCE_CONCEPT_DF = sys.argv[3]
CITATION_CONCEPT_DF = sys.argv[4]
SANKEY_AGGREGATED_DF = sys.argv[5]
SANKEY_TS_DF = sys.argv[6]

def get_vis_doi_concept_dic(DF, LEVEL): # DF here is OPENALEX_CONCEPT_DF
	vis_levelns_df = DF[DF.Level == LEVEL].reset_index(drop=True)
	max_score_leveln = []
	for group in vis_levelns_df.groupby('DOI'):
		max_score = max(group[1]['Score'])
		df_to_append = group[1][group[1]['Score'] == max_score]
		max_score_leveln.append(df_to_append)
	vis_leveln_df = pd.concat(max_score_leveln, ignore_index=True)
	vis_leveln_doi_concept_dic = dict(
		zip(vis_leveln_df.DOI, vis_leveln_df.Concept))
	return vis_leveln_doi_concept_dic

def get_leveln_df(DF, LEVEL, ID_NAME): 
	"""
	inputs:
		DF is either s REF_DF or CIT_DF
		ID_NAME is either REF_ID_NAME or CIT_ID_NAME
	Returns:
		a dataframe of two columns: 
			1. IEEE VIS papers' DOI
			2. REF/CIT papers' concept
	"""
	dfs = []
	levelns_df = DF[DF.Level == LEVEL]
	# keep only the highest score concept
	for group in levelns_df.groupby(ID_NAME):
		dff = group[1].sort_values(by='Score', ascending=False)
		max_score = max(dff['Score'])
		dff_to_append = dff[dff['Score'] == max_score]
		dfs.append(dff_to_append)

	leveln_df = pd.concat(dfs, ignore_index=True)[['DOI', 'Concept', ID_NAME]]
	return leveln_df

def get_leveln_output_df(DF, VIS_DOI_CONCEPT_DIC, YEAR_DICT, YEAR_KEY, SUFFIX):
	"""
	inputs:
		DF is either REF_LEVELN_DF or CIT_LEVELN_DF
		YEAR_DICT is either DOI_YEAR_DICT or CIT_ID_YEAR_DICT
		YEAR_KEY is either REF_YEAR_KEY, or CIT_YEAR_KEY
		SUFFIX is either REF_SUFFIX or CIT_SUFFIX

	The purpose of this step:
		1. map DOI to IEEE VIS concept
		2. get the year when this citation happens
	"""

	DF['IEEE VIS Concept'] = DF.DOI.apply(
		lambda x: VIS_DOI_CONCEPT_DIC[
			x] if x in VIS_DOI_CONCEPT_DIC.keys() else np.NaN
	)
	DF['Year'] = DF[YEAR_KEY].apply(lambda x: YEAR_DICT[x])
	leveln_df_nonan = DF[DF['IEEE VIS Concept'].notnull()]
	leveln_df_output = leveln_df_nonan.drop(
		columns=['DOI']).reset_index(drop=True)
	if SUFFIX == REF_SUFFIX:
		leveln_df_output['Concept'] = leveln_df_output[
			'Concept'].apply(lambda s: s + REF_SUFFIX)
	else:
		leveln_df_output['Concept'] = leveln_df_output[
			'Concept'].apply(lambda s: s + CIT_SUFFIX)
	leveln_df_output['IEEE VIS Concept'] = leveln_df_output[
		'IEEE VIS Concept'].apply(lambda s: s + "(v)")
	return leveln_df_output

def get_leveln_aggregated(SOURCE, DF, LEVEL): 
	"""
	inputs:
		SOURCE is either 'REF' or 'CIT'
		DF is either REF_LEVELN_OUTPUT or CIT_LEVELN_OUTPUT
	"""
	if SOURCE == 'REF':
		tuples = list(zip(
			DF['Concept'], 
			DF['IEEE VIS Concept'],
		))
	else:
		tuples = list(zip(
			DF['IEEE VIS Concept'],
			DF['Concept'], 
		))
	biconcept_counts = Counter(tuples)
	dic = dict(biconcept_counts)
	sankey_df = pd.DataFrame(dic.items(), columns=['pairs','value'])
	sankey_df['level'] = LEVEL
	sankey_df['source'] = sankey_df.pairs.apply(lambda x: x[0])
	sankey_df['target'] = sankey_df.pairs.apply(lambda x: x[1])
	sankey_df_sorted = sankey_df[
		['source', 'target', 'value', 'level']].sort_values(
		by='value', ascending=False).reset_index(drop=True)
	sankey_df_sorted['rank'] = sankey_df_sorted.index + 1
	return sankey_df_sorted

def get_ts_year_group_data(SOURCE, DF, LEVEL):
	"""
	inputs:
		SOURCE is either 'REF' or 'CIT'
		DF is year_group

	This is much the same as the get_leveln_aggregated() function
	"""
	if SOURCE == 'REF':
		tuples = list(zip(
			DF[1]['Concept'], 
			DF[1]['IEEE VIS Concept'],
		))
	else:
		tuples = list(zip(
			DF[1]['IEEE VIS Concept'],
			DF[1]['Concept'], 
		))
	biconcept_counts = Counter(tuples)
	dic = dict(biconcept_counts)
	sankey_df = pd.DataFrame(dic.items(), columns=['pairs','value'])
	sankey_df['level'] = LEVEL
	sankey_df['source'] = sankey_df.pairs.apply(lambda x: x[0])
	sankey_df['target'] = sankey_df.pairs.apply(lambda x: x[1])
	sankey_df_sorted = sankey_df[
		['source', 'target', 'value', 'level']].sort_values(
		by='value', ascending=False).reset_index(drop=True)
	sankey_df_sorted['rank'] = sankey_df_sorted.index + 1
	sankey_df_sorted['year'] = DF[0]
	return sankey_df_sorted

if __name__ == '__main__':
	VISPUBDATA_PLUS = pd.read_csv(VISPUBDATA_PLUS)
	OPENALEX_CONCEPT_DF = pd.read_csv(OPENALEX_CONCEPT_DF)
	REF_DF = pd.read_csv(REFERENCE_CONCEPT_DF)
	CIT_DF = pd.read_csv(CITATION_CONCEPT_DF)

	REF_ID_NAME = 'Reference OpenAlex ID'
	CIT_ID_NAME = 'Citation Paper OpenAlex ID'

	REF_DF = REF_DF[REF_DF[REF_ID_NAME].notnull()]
	CIT_DF = CIT_DF[CIT_DF[CIT_ID_NAME].notnull()]
	CIT_DF.rename(columns = {'Cited Paper DOI': 'DOI'}, inplace=True)

	DOI_YEAR_DICT = dict(zip(
		VISPUBDATA_PLUS.DOI, VISPUBDATA_PLUS.Year
	))

	CIT_ID_YEAR_DICT = dict(zip(
		CIT_DF[CIT_ID_NAME], CIT_DF['Citation Paper Year']
	))

	REF_YEAR_KEY = 'DOI'
	CIT_YEAR_KEY = CIT_ID_NAME

	# Set parameters
	START_LEVEL = 0
	END_LEVEL = 3
	CUTOFF = 500
	REF_SUFFIX = '(r)'
	CIT_SUFFIX = '(c)'

	# initiate dfs
	REF_LEVELN_AGGREGATED_DFS = []
	CIT_LEVELN_AGGREGATED_DFS = []
	REF_LEVELN_TS_DFS = []
	CIT_LEVELN_TS_DFS = []

	for LEVEL in range(START_LEVEL, END_LEVEL + 1):
		VIS_DOI_CONCEPT_DIC = get_vis_doi_concept_dic(
			OPENALEX_CONCEPT_DF,
			LEVEL
		)

		# REFERENCE -> VIS
		REF_LEVELN_DF = get_leveln_df(
			REF_DF, 
			LEVEL, 
			REF_ID_NAME,
		)
		REF_LEVELN_OUTPUT = get_leveln_output_df(
			REF_LEVELN_DF, 
			VIS_DOI_CONCEPT_DIC, 
			DOI_YEAR_DICT, 
			REF_YEAR_KEY, 
			REF_SUFFIX,
		)
		REF_LEVELN_AGGREGATED = get_leveln_aggregated(
			'REF',
			REF_LEVELN_OUTPUT, 
			LEVEL,
		)

		REF_LEVELN_AGGREGATED_DFS.append(REF_LEVELN_AGGREGATED)

		# TIMESERIES:
		REF_LEVELN_YEAR_GROUP_DFS = []
		for year_group in REF_LEVELN_OUTPUT.groupby('Year'):
			year_group_data = get_ts_year_group_data(
				'REF',
				year_group,
				LEVEL
				)
			REF_LEVELN_YEAR_GROUP_DFS.append(year_group_data)
		REF_LEVELN_TS_DF = pd.concat(
			REF_LEVELN_YEAR_GROUP_DFS,
			ignore_index = True,
		)
		REF_LEVELN_TS_DFS.append(REF_LEVELN_TS_DF)

		# VIS -> CITATION
		CIT_LEVELN_DF = get_leveln_df(
			CIT_DF, 
			LEVEL, 
			CIT_ID_NAME,
		)
		CIT_LEVELN_OUTPUT = get_leveln_output_df(
			CIT_LEVELN_DF, 
			VIS_DOI_CONCEPT_DIC, 
			CIT_ID_YEAR_DICT, 
			CIT_YEAR_KEY, 
			CIT_SUFFIX,
		)
		CIT_LEVELN_AGGREGATED = get_leveln_aggregated(
			'CIT',
			CIT_LEVELN_OUTPUT, 
			LEVEL,
		)

		CIT_LEVELN_AGGREGATED_DFS.append(CIT_LEVELN_AGGREGATED)

		# TIMESERIES:
		CIT_LEVELN_YEAR_GROUP_DFS = []
		for year_group in CIT_LEVELN_OUTPUT.groupby('Year'):
			year_group_data = get_ts_year_group_data(
				'CIT',
				year_group,
				LEVEL,
			)
			CIT_LEVELN_YEAR_GROUP_DFS.append(year_group_data)
		CIT_LEVELN_TS_DF = pd.concat(
			CIT_LEVELN_YEAR_GROUP_DFS,
			ignore_index = True,
		)
		CIT_LEVELN_TS_DFS.append(CIT_LEVELN_TS_DF)

		print(f'level {LEVEL} is done')

	# GET AGGREGATED_DF
	ref_aggregated = pd.concat(
		REF_LEVELN_AGGREGATED_DFS,
		ignore_index = True,
	)
	ref_aggregated['source name'] = 'REF'
	cit_aggregated = pd.concat(
		CIT_LEVELN_AGGREGATED_DFS,
		ignore_index = True,
	)
	cit_aggregated['source name'] = 'VIS'

	aggregated_df = pd.concat(
		[ref_aggregated, cit_aggregated],
		ignore_index = True,
	)

	# GET TS_DF
	ref_timeseries = pd.concat(
		REF_LEVELN_TS_DFS,
		ignore_index = True,
	)
	ref_timeseries['source name'] = 'REF'
	cit_timeseries = pd.concat(
		CIT_LEVELN_TS_DFS,
		ignore_index = True,
	)
	cit_timeseries['source name'] = 'VIS'

	ts_df = pd.concat(
		[ref_timeseries, cit_timeseries],
		ignore_index = True,
	)

	# Write to file
	aggregated_df.to_csv(SANKEY_AGGREGATED_DF, index=False)
	ts_df.to_csv(SANKEY_TS_DF, index=False)

	print('sankey data has been saved!')


	







