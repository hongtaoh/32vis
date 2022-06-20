"""this script generates HT cleaned author df 
"""

import sys
import pandas as pd
import numpy as np
import itertools

MERGED_CNTRY_PREDICTED = sys.argv[1]
MERGED_AFF_TYPE_PREDICTED = sys.argv[2]
HT_CLEANED_AUTHOR_DF = sys.argv[3]

def get_cross_country_dic(df):
	cross_country_dic = {}
	for group in df.groupby('DOI'):
	    DOI = group[0]
	    country_codes = group[1]['Affiliation Country Code'].tolist()
	    num_of_cntry = len(list(set(country_codes)))
	    if num_of_cntry != 1:
	        cross_country_dic[DOI] = True
	    else:
	        cross_country_dic[DOI] = False
	return cross_country_dic

def get_cross_type_dic(df):
	cross_type_dic = {}
	for group in df.groupby('DOI'):
	    DOI = group[0]
	    types = group[1]['Binary Type'].tolist()
	    num_of_types = len(list(set(types)))
	    if num_of_types != 1:
	        cross_type_dic[DOI] = True
	    else:
	        cross_type_dic[DOI] = False
	return cross_type_dic


if __name__ == '__main__':
	# load data
	cntry_df = pd.read_csv(MERGED_CNTRY_PREDICTED)
	type_df = pd.read_csv(MERGED_AFF_TYPE_PREDICTED)

	if cntry_df.shape[0] == type_df.shape[0]:
		print('cntry_df has the same length with type_df')

	# get the column of affiliation type
	aff_types = type_df['Affiliation Type']

	# assign it to cntry_df and reanme columns
	cntry_df = cntry_df.assign(aff_type = aff_types)
	cntry_df.rename(
		columns = {'aff_type': 'Affiliation Type'}, 
		inplace=True
	)

	df = cntry_df.copy()

	# get binary type
	df['Binary Type'] = df['Affiliation Type'].apply(
		lambda x: x if x == 'education' else 'non-education'
	)

	cross_country_dic = get_cross_country_dic(df)
	cross_type_dic = get_cross_type_dic(df)

	df['Cross-type Collaboration'] = df.DOI.apply(
    	lambda x: cross_type_dic[x]
	)
	df['International Collaboration'] = df.DOI.apply(
    	lambda x: cross_country_dic[x]
	)


	df.to_csv(HT_CLEANED_AUTHOR_DF, index=False)

