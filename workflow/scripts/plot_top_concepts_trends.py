"""This script prepares for top concept trends visualization

Note that I kept all concepts assigned to each paper, rather than 
the one with the highest score.

"""

import sys
import numpy as np
import pandas as pd
from collections import Counter

OPENALEX_PAPER_DF = sys.argv[1]
OPENALEX_CONCEPT_DF = sys.argv[2]
TOP_CONCEPTS_TRENDS_DF = sys.argv[3]

def get_year_count_dic(DF): # DF here is openalex_paper_df
	"""I want proportion. So I need first know total number of pubs each year"""
	year_count_df = DF.groupby(
		'Year').size().to_frame('count').reset_index()
	year_count_dic = dict(
		zip(year_count_df['Year'], year_count_df['count']))
	return year_count_dic 

def get_top_concepts_rank_and_total(DF, LEVEL, CUTOFF): # DF here is OPENALEX_CONCEPT_DF
	"""get the top concepts, its rank, and its historical total
	"""
	# filter by specific level
	lvl = DF[DF.Level == LEVEL]

	# get the total frequency of the concepts within that level
	lvl_df = lvl.groupby(['Concept', 'Concept ID']).size().to_frame(
		'frequency').reset_index().sort_values(
		by='frequency', ascending=False).head(CUTOFF)

	# get the rank of each of the top 10 concepts within that level
	# generate two dics: one for rank, and the other for total
	lvl_df['rank'] = range(1, CUTOFF+1)
	top_concepts = lvl_df['Concept']
	concept_rank_dic = dict(zip(lvl_df['Concept'], lvl_df['rank']))
	concept_historical_total_dic = dict(zip(lvl_df['Concept'], lvl_df['frequency']))
	return top_concepts, concept_rank_dic, concept_historical_total_dic


def get_ts_for_top(DF, TOP_CONCEPTS): # DF here is OPENALEX_CONCEPT_DF
	"""
	get timeseries data for top concepts

	Returns:
		a dataframe where in each row I have a concept, a year, and 
		the total frequency of that concept in that year

	"""

	top_concepts_ts_df = DF[DF.Concept.isin(TOP_CONCEPTS)].groupby(
		['Concept', 'Year']).size().to_frame(
		'Concept Yearly Frequency').reset_index()
	return top_concepts_ts_df


def update_dfs(
	DF, 
	i, 
	TOP_RANK_DIC, 
	TOP_TOTAL_DIC, 
	YEAR_COUNT_DIC,
	DFS
	): # DF here is TOP_CONCEPTS_TS_DF
	
	LEVEL = i
	dfss = []
	start = 1990 ; end = 2021
	year_idx = range(start, end+1)

	for group in DF.groupby('Concept'):
		"""Normalize each concept in each level by the same time range, i.e., 1990-2021"""
		year_frequency_dic = dict(
			zip(group[1]['Year'], group[1]['Concept Yearly Frequency']))
		concepts = [group[1].iloc[0, :].Concept] * len(year_idx)
		frequencies = [
			year_frequency_dic[
			x] if x in year_frequency_dic.keys() else 0 for x in year_idx]
		time_series_df = pd.DataFrame(
			list(zip(concepts, year_idx, frequencies)), 
			columns = [f'concept_{LEVEL}', f'year_{LEVEL}', f'yearly frequency_{LEVEL}'])
		time_series_df[f'rank_{LEVEL}'] = time_series_df[f'concept_{LEVEL}'].apply(
			lambda x: TOP_RANK_DIC[x])
		time_series_df[f'level_{LEVEL}'] = LEVEL
		time_series_df[f'concept historical total_{LEVEL}'] = time_series_df[
			f'concept_{LEVEL}'].apply(
			lambda x: TOP_TOTAL_DIC[x])
		time_series_df[f'yearly vis total_{LEVEL}'] = time_series_df[f'year_{LEVEL}'].apply(
			lambda x: YEAR_COUNT_DIC[x])
		time_series_df[f'proportion_{LEVEL}'] = time_series_df[
			f'yearly frequency_{LEVEL}'] / time_series_df[f'yearly vis total_{LEVEL}']
		# time_series_df is for each concept within each level
		# dfss is to contain all concepts data within a level
		dfss.append(time_series_df.reset_index(drop=True))
	level_df_to_append = pd.concat(dfss, ignore_index = True)
	level_df_to_append.sort_values(by=[f'rank_{LEVEL}', f'year_{LEVEL}'], inplace=True)
	DFS.append(level_df_to_append.reset_index(drop=True))


if __name__ == '__main__':
	# Set parameters
	START_LEVEL = 0
	END_LEVEL = 3
	# CUTOFF = 30
	CUTOFF = 10

	OPENALEX_PAPER_DF = pd.read_csv(OPENALEX_PAPER_DF)
	OPENALEX_CONCEPT_DF = pd.read_csv(OPENALEX_CONCEPT_DF)

	YEAR_COUNT_DIC = get_year_count_dic(OPENALEX_PAPER_DF)

	DFS = []
	for i in range(START_LEVEL, END_LEVEL+1):
		TOP_CONCEPTS, TOP_RANK_DIC, TOP_TOTAL_DIC = get_top_concepts_rank_and_total(
			OPENALEX_CONCEPT_DF, 
			i, 
			CUTOFF
		)

		TOP_CONCEPTS_TS_DF = get_ts_for_top(
			OPENALEX_CONCEPT_DF, TOP_CONCEPTS
		)
		update_dfs(
		TOP_CONCEPTS_TS_DF, 
		i, 
		TOP_RANK_DIC, 
		TOP_TOTAL_DIC, 
		YEAR_COUNT_DIC,
		DFS
		)

	# concat, validate, and write to file

	dff = pd.concat(DFS, axis=1)

	print(dff['year_1'].tolist() == dff['year_2'].tolist())
	print(dff['year_1'].tolist() == dff['year_3'].tolist())
	print(dff['rank_1'].tolist() == dff['rank_3'].tolist())
	print(dff['rank_1'].tolist() == dff['rank_2'].tolist())

	dff.to_csv(TOP_CONCEPTS_TRENDS_DF, index = False)






