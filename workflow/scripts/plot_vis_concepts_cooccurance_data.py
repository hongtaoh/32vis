"""This script prepares for vis concept cooccurance visualization"""

import sys
import numpy as np
import pandas as pd
import itertools
from collections import Counter

OPENALEX_CONCEPT_DF = sys.argv[1]
AGGREGATED_COOCCURANCE_DF = sys.argv[2]
TS_AGGREGATED_COOCCURANCE_DF = sys.argv[3]

def get_level_df(DF, LEVEL):
	# subset by level
	level_df = DF[DF.Level == LEVEL].reset_index(drop=True)
	return level_df

def get_dic(LEVEL_DF): # DF here is OPENALEX_CONCEPT_DF
	"""get the dictionary of biconcept counts"""

	# initiate a tuple list
	tuple_list = []

	# for each ieeevis paper, get combinations of level concepts if more than two 
	# level concepts exist
	for group in LEVEL_DF.groupby('DOI'):
		concepts = list(set(group[1].Concept))
		if len(concepts) > 1:
			tuples = [x for x in itertools.combinations(concepts, 2)]
			tuple_list.append(tuples)

	# get biconcepts dictionary
	biconcepts = list(itertools.chain(*tuple_list))
	biconcept_counts_dic = dict(Counter(biconcepts))

	return biconcept_counts_dic

def update_data(DIC, LEVEL, CUTOFF, DATA): # DIC: biconcept_counts_dic
	# DATA: cooccurance_aggregated_data
	chord_df = pd.DataFrame(DIC.items(), columns=['pairs','value'])
	chord_df['level'] = LEVEL
	chord_df['source'] = chord_df.pairs.apply(lambda x: x[0])
	chord_df['target'] = chord_df.pairs.apply(lambda x: x[1])
	chord_df = chord_df[
		['source', 'target', 'value', 'level']].sort_values(
		by='value', ascending=False).reset_index(drop=True)
	chord_df = chord_df[chord_df['value'] >= CUTOFF]
	DATA.append(chord_df)

def update_ts_data(DIC, YEAR, LEVEL, CUTOFF, DATA):
	"""get timeseries chord dataframe"""
	chord_df = pd.DataFrame(DIC.items(), columns=['pairs','value'])
	chord_df['year'] = YEAR
	chord_df['level'] = LEVEL
	chord_df['source'] = chord_df.pairs.apply(lambda x: x[0])
	chord_df['target'] = chord_df.pairs.apply(lambda x: x[1])
	chord_df = chord_df[
		['source', 'target', 'value', 'year', 'level']].sort_values(
		by='value', ascending=False).reset_index(drop=True)
	chord_df = chord_df[chord_df['value'] >= CUTOFF]
	DATA.append(chord_df)


if __name__ == '__main__':
	OPENALEX_CONCEPT_DF = pd.read_csv(OPENALEX_CONCEPT_DF)

	"""set parameters """ 

	CUTOFF = 1 # cutoff number for cooccurance
	START = 0 # top level
	END = 3 # lowest level 

	"""Get Aggregated data """

	# Aggregated data, involving data of all levles
	cooccurance_aggregated_data = []

	# iterate through all levels
	for LEVEL in range(START, END + 1):
		LEVEL_DF = get_level_df(OPENALEX_CONCEPT_DF, LEVEL)
		biconcept_counts_dic = get_dic(LEVEL_DF)
		update_data(
			biconcept_counts_dic, LEVEL, CUTOFF, cooccurance_aggregated_data)

	# write to file
	aggregated_df = pd.concat(cooccurance_aggregated_data, ignore_index=True)
	aggregated_df.to_csv(AGGREGATED_COOCCURANCE_DF, index=False)


	"""Get Timeseries data """

	cooccurance_timeseries_aggregated_data = []

	for LEVEL in range(START, END + 1):

		# initiate time series data for each level
		# it will collect each year's data within the current LEVEL
		cooccurance_timeseries_data = []

		LEVEL_DF = get_level_df(OPENALEX_CONCEPT_DF, LEVEL)

		for YEAR_GROUP in LEVEL_DF.groupby('Year'):
			biconcept_counts_dic = get_dic(YEAR_GROUP[1])
			update_ts_data(
				biconcept_counts_dic, 
				YEAR_GROUP[0], 
				LEVEL, 
				CUTOFF, 
				cooccurance_timeseries_data
			)

		# this is the final data for each level
		cooccurance_timeseries_df = pd.concat(
			cooccurance_timeseries_data, ignore_index=True)

		# append this level's data to aggregated data list
		cooccurance_timeseries_aggregated_data.append(cooccurance_timeseries_df)

	# write to file
	ts_aggregated_df = pd.concat(
		cooccurance_timeseries_aggregated_data, ignore_index=True)
	ts_aggregated_df.to_csv(TS_AGGREGATED_COOCCURANCE_DF, index=False)
