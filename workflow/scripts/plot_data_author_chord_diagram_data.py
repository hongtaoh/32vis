"""This script prepares for author collaboration chord diagram data"""

import sys
import pandas as pd
import itertools
from collections import Counter

HT_CLEANED_AUTHOR_DF = sys.argv[1]
AUTHOR_CHORD_DF = sys.argv[2]
TS_AUTHOR_CHORD_DF = sys.argv[3]

def get_dic(DF): # DF here is HT_CLEANED_AUTHOR_DF
	"""get the dictionary of bicode counts"""
	tuple_list = []
	for group in DF.groupby('DOI'):
		country_codes = list(set(group[1]['Affiliation Country Code']))
		if len(country_codes) > 1:
			tuples = [x for x in itertools.combinations(country_codes, 2)]
			tuple_list.append(tuples)
	bicode = list(itertools.chain(*tuple_list))
	bicode_counts = Counter(bicode)
	bicode_counts_dic = dict(bicode_counts)
	return bicode_counts_dic 

def get_chord_df(DIC): # DIC here is bicode_counts_dic
	"""
	Return:
		A dataframe containig three columns: source, targe, value.
		Even though I am using `source`, and `target`, this is an undirected ntework. 
	"""
	chord_df = pd.DataFrame(DIC.items(), columns=['pairs','value'])
	chord_df['source'] = chord_df.pairs.apply(lambda x: x[0])
	chord_df['target'] = chord_df.pairs.apply(lambda x: x[1])
	chord_df_sorted = chord_df[
		['source', 'target', 'value']].sort_values(
		by='value', ascending=False).reset_index(drop=True)
	return chord_df_sorted

def get_ts_chord_df(DF, ts_chord_data): # DF here is HT_CLEANED_AUTHOR_DF
	"""
	get timeseries data. groupby year first. get each year's data and then concatenate
	"""
	for year_group in DF.groupby("Year"):
		bicode_counts_dic = get_dic(year_group[1])
		chord_df = pd.DataFrame(
			bicode_counts_dic.items(), columns=['pairs','value'])
		chord_df['year'] = year_group[0]
		chord_df['source'] = chord_df.pairs.apply(lambda x: x[0])
		chord_df['target'] = chord_df.pairs.apply(lambda x: x[1])
		chord_df_sorted = chord_df[
			['source', 'target', 'value', 'year']].sort_values(
			by='value', ascending=False).reset_index(drop=True)
		ts_chord_data.append(chord_df_sorted)
	ts_chord_df = pd.concat(
		ts_chord_data, ignore_index=True)
	return ts_chord_df 

def rename_countries(DF):
	"""to convert country codes to name"""
	DF.replace({
		'CH': 'Switzerland',
		'CN': 'China',
		'DE': 'Germany',
		'CA': 'Canada',
		'FR': 'France',
		'NL': 'Netherlands',
		'AT': 'Austria',
		'AU': 'Australia',
	},
		inplace=True
	)
	return DF 

if __name__ == '__main__':
	HT_CLEANED_AUTHOR_DF = pd.read_csv(HT_CLEANED_AUTHOR_DF)
	ts_chord_data = []
	bicode_counts_dic = get_dic(HT_CLEANED_AUTHOR_DF)
	chord_df = get_chord_df(bicode_counts_dic)
	chord_df.to_csv(AUTHOR_CHORD_DF, index=False)
	ts_chord_df = get_ts_chord_df(HT_CLEANED_AUTHOR_DF, ts_chord_data)
	ts_chord_df.to_csv(TS_AUTHOR_CHORD_DF, index=False)






