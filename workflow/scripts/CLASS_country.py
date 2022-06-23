"""build classification model for country code

"""

import sys
import pandas as pd
import numpy as np
import re
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import accuracy_score, classification_report
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import precision_recall_fscore_support as multi_score
from collections import Counter
from bs4 import BeautifulSoup

def get_simple_df(fname):
	"""
		- remove nan, 
		- get only two target columns, i.e., raw string and aff type
		- drop duplicates
	"""
	raw_string = 'Raw Affiliation String'
	aff_type = 'First Institution Country Code'
	df = pd.read_csv(fname)
	df = df[(df[raw_string].notnull()) & (df[aff_type].notnull())]
	df = df[[raw_string, aff_type]]
	df = df.drop_duplicates()
	return df

def get_df(cit_author, ref_author, oa_author):
	"""concatenate, drop_duplicates, reset index, rename columns,
		factorize label_str

	Returns:
		the df used for model training and testing. It contains three columns:
			1. aff, which is pre-processed strings of affiliations
			2. label_str, which is country codes in strings,
			3. label: which is factorized version of country codes
	"""

	df = pd.concat(
		[oa_author, ref_author, cit_author], ignore_index = True
		).drop_duplicates().reset_index(drop=True)
	df.columns = ['aff', 'label_str']
	df = df.assign(label = pd.factorize(df['label_str'])[0])
	return df 

def get_dicts(df):
	"""get two dicts; id <--> cntry
	"""
	cntry_to_id = dict(zip(df.label_str, df.label))
	id_to_cntry = dict(zip(df.label, df.label_str))
	return cntry_to_id, id_to_cntry

def clean_text(text):
    """
    Takes a string and returns a string
    """
    # remove html tags, lowercase, remove nonsense, remove non-letter
    aff = BeautifulSoup(text, "lxml").text 
    aff = aff.lower()
    aff = re.sub(r'xa0|#n#‡#n#|#tab#|#r#|\[|\]', "", aff)
    aff = re.sub(r'[^a-z]+', ' ', aff)
    return aff

def logist_regression(df):
	'''
	Input: 
		df: df
	Returns:
		logreg: logistic regression model
	'''
	X = df.aff
	y = df.label
	X_train, X_test, y_train, y_test = train_test_split(
		X, y, test_size=0.2, random_state = 42)
	logreg = Pipeline([('vect', CountVectorizer(stop_words='english', min_df = 5)),
				('clf', LogisticRegression(max_iter=600)),
			   ])
	print('model training now...')
	logreg.fit(X_train, y_train)

	y_pred = logreg.predict(X_test)

	target_names = list(set([id_to_cntry[x] for x in y_test]))
	
	f = open(CNTRY_CLASSIFICATION_REPORT,'a')
	f.write('The following is the result for affiliation country code classification' + '\n')
	f.write('accuracy %s' % accuracy_score(y_pred, y_test))
	# f.write('\n')
	# f.write(classification_report(y_test, y_pred, target_names=target_names))

	return logreg

def get_processed_merged_author(DF, LOGREG):
	'''
	Input: 
		- DF: merged
		- LOGREG
	Returns:
		- DF with cntry classification results
	'''
	# clean text for affs to be predicted
	DF['IEEE Author Affiliation Filled'] = DF[
		'IEEE Author Affiliation Filled'].apply(clean_text)
	pred = LOGREG.predict(DF['IEEE Author Affiliation Filled'])
	results = [id_to_cntry[x] for x in pred]
	DF['country_code_results'] = results
	DF = DF.assign(country_code_results_updated = 
	    np.where(DF['First Institution Country Code By Hand'].notnull(), 
	         DF['First Institution Country Code By Hand'],
	         DF['country_code_results']
	        ))
	return DF

if __name__ == '__main__':

	CIT_AUTHOR = sys.argv[1]
	REF_AUTHOR = sys.argv[2]
	# openalex author df for VIS papers:
	OA_AUTHOR = sys.argv[3]
	MERGED_AUTHOR = sys.argv[4]
	MERGED_CNTRY_PREDICTED = sys.argv[5]
	CNTRY_CLASSIFICATION_REPORT = sys.argv[6]

	# load datasets:
	cit_author = get_simple_df(CIT_AUTHOR)
	ref_author = get_simple_df(REF_AUTHOR)
	oa_author = get_simple_df(OA_AUTHOR)
	merged = pd.read_csv(MERGED_AUTHOR)

	# get df for model trainig and testing
	df = get_df(cit_author, ref_author, oa_author)

	# clean affiliation texts 
	df['aff'] = df['aff'].apply(clean_text)

	# get dicts
	cntry_to_id, id_to_cntry = get_dicts(df)

	# get logreg
	logreg = logist_regression(df)

	merged_processed = get_processed_merged_author(merged, logreg)

	# export merged_processed
	cols_to_keep = [
		'Year',
		'DOI',
		'Title',
		'IEEE Number of Authors',
		'IEEE Author Position', 
		'IEEE Author Name',
		'OpenAlex Author ID',
		'IEEE Author Affiliation Filled',
		'country_code_results_updated', 
		]
	col_renamer = {
		'Year':'Year',
		'DOI':'DOI',
		'Title':'Title',
		'IEEE Number of Authors':'Number of Authors',
		'IEEE Author Position':'Author Position', 
		'IEEE Author Name':'Author Name',
		'OpenAlex Author ID':'OpenAlex Author ID',
		'IEEE Author Affiliation Filled':'Affiliation Name',
		'country_code_results_updated':'Affiliation Country Code', 
		}
	merged_cntry_predicted = merged_processed[cols_to_keep]
	merged_cntry_predicted.rename(columns = col_renamer).to_csv(
		MERGED_CNTRY_PREDICTED, index = False
	)