"""build classification model for affiliation type

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
from bs4 import BeautifulSoup

def get_simple_df(fname):
	"""
		- remove nan, 
		- get only two target columns, i.e., raw string and aff type
		- drop duplicates
	"""
	raw_string = 'Raw Affiliation String'
	aff_type = 'First Institution Type'
	df = pd.read_csv(fname)
	df = df[(df[raw_string].notnull()) & (df[aff_type].notnull())]
	df = df[[raw_string, aff_type]]
	df = df.drop_duplicates()
	return df

def get_df(cit_author, ref_author, oa_author):
	"""concatenate, drop_duplicates, reset index, rename columns,
		factorize label_str

	Returns:
		the df used for model training and testing. It contains five columns:
			1. aff, which is pre-processed strings of affiliations
			2. label_str, which is country codes in strings,
			3. label: which is factorized version of country codes
			4. binary_label_str
			5. binary_label
	"""

	df = pd.concat(
		[oa_author, ref_author, cit_author], ignore_index = True
		).drop_duplicates().reset_index(drop=True)
	df.columns = ['aff', 'label_str']
	df = df.assign(label = pd.factorize(df['label_str'])[0])
	df = df.assign(binary_label_str = np.where(
		df.label_str == 'education', 'education', 'non-education'))
	df = df.assign(binary_label = pd.factorize(df['binary_label_str'])[0])
	return df 

def get_dicts(df):
	"""get four dicts; id <--> type, for both binary and multiclass
	"""
	multi_type_to_id = dict(zip(df.label_str, df.label))
	id_to_multi_type = dict(zip(df.label, df.label_str))
	binary_type_to_id = dict(zip(df.binary_label_str, df.binary_label))
	id_to_binary_type = dict(zip(df.binary_label, df.binary_label_str))
	return multi_type_to_id, id_to_multi_type, binary_type_to_id, id_to_binary_type

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

def logist_regression(df, LABEL):
	'''
	Input: 
		df: df
		LABEL: 'label' if multiclass and 'binary_label' if binary
	Returns:
		logreg: logistic regression classifier (model)

	'''
	X = df.aff
	y = df[LABEL]
	X_train, X_test, y_train, y_test = train_test_split(
		X, y, test_size=0.2, random_state = 42)
	logreg = Pipeline([('vect', CountVectorizer(stop_words='english', min_df = 2)),
				('clf', LogisticRegression(max_iter=600)),
			   ])
	print('model training now...')
	logreg.fit(X_train, y_train)

	y_train_pred = logreg.predict(X_train)
	y_test_pred = logreg.predict(X_test)

	target_names = list(set(df.label_str)) if LABEL == 'label' else list(set(df.binary_label_str))
	logreg_type = 'multiclass classification' if LABEL == 'label' else 'binary classification'
	
	f = open(TYPE_CLASSIFICATION_REPORT,'a')
	f.write('The following is the result for aff type' + ' : ' + logreg_type + '\n')
	f.write('Test set accuracy %s' % accuracy_score(y_test, y_test_pred))
	f.write('\n')
	precision, recall, fscore, support = multi_score(
		y_test, 
		y_test_pred, 
		average='weighted'
	)
	f.write('precision: {}'.format(precision))
	f.write('\n')
	f.write('recall: {}'.format(recall))
	f.write('\n')
	f.write('fscore: {}'.format(fscore))
	f.write('\n')
	f.write('support: {}'.format(support))
	f.write('\n')
	f.write('\n')
	f.write('Training set accuracy %s' % accuracy_score(y_train, y_train_pred))
	# f.write('\n')
	# f.write(classification_report(y_test, y_test_pred, target_names=target_names))
	f.write('\n')
	f.write('\n')

	f.close()

	return logreg

def get_processed_merged_author(DF, LOGREG_MULTI, LOGREG_BINARY):
	'''
	Input: 
		- DF: merged
		- LOGREG_MULTI
		- LOGREG_BINARY
	Returns:
		- DF with binary and multiclass classification results
	'''
	# clean text for affs to be predicted
	DF['IEEE Author Affiliation Filled_Processed'] = DF[
		'IEEE Author Affiliation Filled'].apply(clean_text)
	pred_binary = LOGREG_BINARY.predict(DF['IEEE Author Affiliation Filled_Processed'])
	pred_binary_type = [id_to_binary_type[x] for x in pred_binary]
	pred_multi = LOGREG_MULTI.predict(DF['IEEE Author Affiliation Filled_Processed'])
	pred_multi_type = [id_to_multi_type[x] for x in pred_multi]
	DF['aff_type_results_binary'] = pred_binary_type
	DF['aff_type_results_multiclass'] = pred_multi_type
	# use type by hand if exists
	DF = DF.assign(aff_type_results_binary_updated = 
	    np.where(DF['Binary Institution Type By Hand'].notnull(), 
	         DF['Binary Institution Type By Hand'],
	         DF['aff_type_results_binary']
	        ))
	# use type by hand if exists
	DF = DF.assign(aff_type_results_multiclass_updated = 
	    np.where(DF['First Institution Type By Hand'].notnull(), 
	         DF['First Institution Type By Hand'],
	         DF['aff_type_results_multiclass']
	        ))
	return DF

if __name__ == '__main__':

	CIT_AUTHOR = sys.argv[1]
	REF_AUTHOR = sys.argv[2]
	# openalex author df for VIS papers:
	OA_AUTHOR = sys.argv[3]
	MERGED_AUTHOR = sys.argv[4]
	MERGED_AFF_TYPE_PREDICTED = sys.argv[5]
	TYPE_CLASSIFICATION_REPORT = sys.argv[6]

	# load datasets:
	cit_author = get_simple_df(CIT_AUTHOR)
	ref_author = get_simple_df(REF_AUTHOR)
	oa_author = get_simple_df(OA_AUTHOR)
	merged = pd.read_csv(MERGED_AUTHOR)

	# get df for model trainig and testing
	df = get_df(cit_author, ref_author, oa_author)

	# clean affiliation texts 
	df['aff'] = df['aff'].apply(clean_text)

	# drop duplicates after text pre-processing
	df = df.drop_duplicates()
	f = open(TYPE_CLASSIFICATION_REPORT,'a')
	f.write(f'there are {df.shape[0]} training examples in aff type classification.')
	f.write('\n')
	f.write('\n')
	f.close()

	# get dicts
	multi_type_to_id, id_to_multi_type, binary_type_to_id, id_to_binary_type = get_dicts(df)

	# get logreg
	logreg_multi = logist_regression(df, 'label')
	logreg_binary = logist_regression(df, 'binary_label')

	merged_processed = get_processed_merged_author(merged, logreg_multi, logreg_binary)

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
		'aff_type_results_multiclass_updated', 
		'aff_type_results_binary_updated', 
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
		'aff_type_results_multiclass_updated':'Multiclass Affiliation Type', 
		'aff_type_results_binary_updated':'Binary Affiliation Type',
		}
	merged_aff_type_predicted = merged_processed[cols_to_keep]
	merged_aff_type_predicted.rename(columns = col_renamer).to_csv(
		MERGED_AFF_TYPE_PREDICTED, index=False
	)