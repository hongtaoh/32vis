"""this script generates cleaned paper df. Basically to gather all useful data about each
individual papers and put it into a single csv file. 
"""

import sys
import pandas as pd
import numpy as np
from functools import reduce 

PAPER_TO_STUDY = sys.argv[1]
VISPUBDATA_PLUS = sys.argv[2]
OPENALEX_PAPER_DF = sys.argv[3]
CLEANED_AUTHOR_DF = sys.argv[4]
GSCHOLAR_DATA = sys.argv[5]
AWARD_PAPER_DF = sys.argv[6]
CLEANED_PAPER_DF = sys.argv[7]

def get_vispd(VISPUBDATA_PLUS, PAPER_TO_STUDY):
	cols = [
		'Conference',
		'Year',
		'Title',
		'DOI',
		'FirstPage',
		'LastPage',
		'PaperType',
	]
	vispd = VISPUBDATA_PLUS[
		VISPUBDATA_PLUS.DOI.isin(PAPER_TO_STUDY)].loc[:, cols].reset_index(drop=True)
	vispd.loc[vispd.Year == 2021, 'PaperType'] = 'J'
	return vispd 

def get_alex(OPENALEX_PAPER_DF):
	cols = [
		'DOI',
		'OpenAlex Year',
		'OpenAlex Publication Date',
		'OpenAlex ID',
		'OpenAlex Venue Name',
		'OpenAlex First Page',
		'OpenAlex Last Page',
		'Number of Pages',
		'Number of References',
		'Number of Concepts',
		'Number of Citations',
	]
	alex = OPENALEX_PAPER_DF.loc[:, cols]
	return alex 

def get_authors(CLEANED_AUTHOR_DF):
	cols = [
		'DOI',
		'Number of Authors',
		'Cross-type Collaboration',
		'International Collaboration',
		'With US Authors',
	]
	# create the column of "With US Authors"
	for doi in list(set(CLEANED_AUTHOR_DF.DOI)):
		if 'US' in CLEANED_AUTHOR_DF[
			CLEANED_AUTHOR_DF.DOI == doi]['Affiliation Country Code'].tolist():
			CLEANED_AUTHOR_DF.loc[CLEANED_AUTHOR_DF.DOI == doi, 'With US Authors'] = True
		else:
			CLEANED_AUTHOR_DF.loc[CLEANED_AUTHOR_DF.DOI == doi, 'With US Authors'] = False
	CLEANED_AUTHOR_DF.drop_duplicates(subset=['DOI'], inplace=True)
	authors = CLEANED_AUTHOR_DF.loc[:, cols].reset_index(drop=True) 
	# create the column of both cross-type and cross-country collaboration
	authors['Both Cross-type and Cross-country Collaboration'] = authors[
		'Cross-type Collaboration'] * authors['International Collaboration']
	# rename column
	authors.rename(
		columns={'International Collaboration': 'Cross-country Collaboration'},
		inplace=True
	)
	return authors 

def get_gscholar(GSCHOLAR_DATA):
	cols = [
		'DOI',
		'IEEE Title',
		'Citation Counts on Google Scholar',
	]
	gscholar = GSCHOLAR_DATA.loc[:, cols]
	return gscholar

def get_df_merged(dfs):
	df_merged = reduce(lambda left,right: pd.merge(left,right,on='DOI'), dfs)
	return df_merged

def get_award_dicts(AWARD_PAPER_DF):
	awards = AWARD_PAPER_DF[AWARD_PAPER_DF.Award != 'TT']
	kwargs = {'Track Updated': np.where(awards.Year == 2021, 'VIS', awards.Track)}
	awards = awards.assign(**kwargs)
	award_dois = awards.DOI.tolist()
	award_names = awards.Award.tolist()
	award_tracks = awards['Track Updated'].tolist()
	doi_award_name_dict = dict(zip(award_dois, award_names))
	doi_award_track_dict = dict(zip(award_dois, award_tracks))
	return award_dois, doi_award_name_dict, doi_award_track_dict

def get_df_final(df_merged, award_dois, doi_award_name_dict, doi_award_track_dict):
	df_merged['Award'] = df_merged['DOI'].apply(
		lambda x: True if x in award_dois else False
	)
	df_merged['Award Name'] = df_merged['DOI'].apply(
		lambda x: doi_award_name_dict[x] if x in award_dois else np.nan)
	df_merged['Award Track'] = df_merged['DOI'].apply(
		lambda x: doi_award_track_dict[x] if x in award_dois else np.nan)
	df_final = df_merged
	return df_final

def main():
	# process data
	vispd = get_vispd(VISPUBDATA_PLUS, PAPER_TO_STUDY)
	alex = get_alex(OPENALEX_PAPER_DF)
	authors = get_authors(CLEANED_AUTHOR_DF)
	gscholar = get_gscholar(GSCHOLAR_DATA)
	# merge data
	dfs = [vispd, alex, authors, gscholar]
	df_merged = get_df_merged(dfs)
	# get award data
	award_dois, doi_award_name_dict, doi_award_track_dict = get_award_dicts(AWARD_PAPER_DF)
	df_final = get_df_final(
		df_merged, award_dois, doi_award_name_dict, doi_award_track_dict)
	# write to file
	df_final.to_csv(CLEANED_PAPER_DF, index=False)

if __name__ == '__main__':
	# load data
	VISPUBDATA_PLUS = pd.read_csv(VISPUBDATA_PLUS)
	PAPER_TO_STUDY = pd.read_csv(PAPER_TO_STUDY, header=None)[0].tolist()
	OPENALEX_PAPER_DF = pd.read_csv(OPENALEX_PAPER_DF)
	CLEANED_AUTHOR_DF = pd.read_csv(CLEANED_AUTHOR_DF)
	GSCHOLAR_DATA = pd.read_csv(GSCHOLAR_DATA)
	AWARD_PAPER_DF = pd.read_csv(AWARD_PAPER_DF)
	main()

