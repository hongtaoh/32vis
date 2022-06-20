"""build classification model for affiliation type

"""

import sys
import pandas as pd
import numpy as np
import re
from io import StringIO
from html.parser import HTMLParser
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import precision_recall_fscore_support as multi_score

CIT_AUTHOR = sys.argv[1]
REF_AUTHOR = sys.argv[2]
# openalex author df for VIS papers:
OA_AUTHOR = sys.argv[3]
MERGED_AUTHOR = sys.argv[4]
MERGED_AFF_TYPE_PREDICTED = sys.argv[5]

def get_simple_df(fname):
	"""
		- remove nan, 
		- get only two target columns, i.e., raw string and country code
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
		factorize label_raw

	Returns:
		the df used for model training and testing. It contains three columns:
			1. aff, which is pre-processed strings of affiliations
			2. label_raw, which is country codes in strings,
			3. label: which is factorized version of country codes
	"""

	df = pd.concat(
		[oa_author, ref_author, cit_author], ignore_index = True
		).drop_duplicates().reset_index(drop=True)
	df.columns = ['aff', 'label_raw']
	df = df.assign(label = pd.factorize(df['label_raw'])[0])
	return df 

def get_dicts(df):
	"""get two dicts, one for cntry to id, and the other for id to cntry
	"""
	label_num_df = df[
		['label_raw', 'label']].drop_duplicates().sort_values(by='label')
	countries = label_num_df['label_raw'].tolist()
	ids = label_num_df['label'].tolist()
	cntry_to_id = dict(zip(countries, ids))
	id_to_cntry = dict(zip(ids, countries))
	return cntry_to_id, id_to_cntry

# scrip html tags and entities in titles
# source: https://stackoverflow.com/a/925630
class MLStripper(HTMLParser):
	def __init__(self):
		super().__init__()
		self.reset()
		self.strict = False
		self.convert_charrefs= True
		self.text = StringIO()
	def handle_data(self, d):
		self.text.write(d)
	def get_data(self):
		return self.text.getvalue()

def strip_tags(html):
	s = MLStripper()
	s.feed(html)
	return s.get_data()


def clean_texts(df, col_name):
	"""
	Returns:
		affs, which is cleaned version ready for trainig and testing.
			type: list of (cleaned) strings
	"""
	# lowercase, remove html tags, remove nonsense, remove non-letter
	affs = df[col_name].tolist()
	affs = [x.lower() for x in affs]
	affs = [strip_tags(x) for x in affs]
	affs = [re.sub(r'xa0|#n#‡#n#|#tab#|#r#|\[|\]', "", x) for x in affs]
	affs = [re.sub(r'[^A-Za-z]+', ' ', x) for x in affs]
	return affs


def get_model(X_train, X_test, y_train, y_test):
	"""get vectorizer and classifier"""
	# Convert words to vector of numbers 
	vectorizer = CountVectorizer(stop_words='english')
	vectorizer.fit(X_train)

	X_train = vectorizer.transform(X_train)
	X_test  = vectorizer.transform(X_test)

	classifier = LogisticRegression(max_iter=400)
	print('training model now...')
	classifier.fit(X_train, y_train)

	return vectorizer, X_train, X_test, classifier 

def get_processed_merged_author(merged, vectorizer, classifier, id_to_cntry):
	affsP = clean_texts(merged, 'IEEE Author Affiliation Filled')
	if len(affsP) == merged.shape[0]:
		print('length of affsP is equal to that of merged shape[0]')
	X_to_predict = vectorizer.transform(affsP)
	predicted_results = classifier.predict(X_to_predict)
	results = [id_to_cntry[x] for x in predicted_results]
	merged['aff_type_results'] = results
	return merged 

if __name__ == '__main__':

	# load datasets:
	cit_author = get_simple_df(CIT_AUTHOR)
	ref_author = get_simple_df(REF_AUTHOR)
	oa_author = get_simple_df(OA_AUTHOR)
	merged = pd.read_csv(MERGED_AUTHOR)

	# get df for model trainig and testing
	df = get_df(cit_author, ref_author, oa_author)

	# get two dicts
	cntry_to_id, id_to_cntry = get_dicts(df)

	# get affs and labels 
	affs = clean_texts(df, 'aff')

	# get labels, a numpy array of numbers representing country codes
	labels = np.array(df['label'])

	# split
	X_train, X_test, y_train, y_test = train_test_split(
		affs, labels, test_size = 0.20, random_state = 42
	)

	# classifier
	vectorizer, X_train, X_test, classifier = get_model(
		X_train, X_test, y_train, y_test)

	# report accurcy score 
	print("aff type classifier:")

	score = classifier.score(X_test, y_test)
	print("Test set accuracy:", score)

	predictions = classifier.predict(X_test)

	score = classifier.score(X_train, y_train)
	print("Train set accuracy:", score)

	precision, recall, fscore, support = multi_score(
		y_test, 
		predictions, 
		average='weighted', 
		labels=np.unique(predictions)
	)

	print('precision: {}'.format(precision))
	print('recall: {}'.format(recall))
	print('fscore: {}'.format(fscore))
	print('support: {}'.format(support))

	merged_processed = get_processed_merged_author(
		merged, vectorizer, classifier, id_to_cntry)

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
		'aff_type_results', 
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
		'aff_type_results':'Affiliation Type', 
		}
	merged_aff_type_predicted = merged_processed[cols_to_keep]
	merged_aff_type_predicted.rename(columns = col_renamer).to_csv(
		MERGED_AFF_TYPE_PREDICTED, index=False
	)





