"""get merged_author_df

input: ieee_author_df, openalex_author_df, papers_to_study

output: merged_author_df

Explanation:
	In this notebook, I first compared the number of authors in IEEE and OpenAlex. I checked PDFs and confirmed 
	that IEEE was wrong in one case, and missed data in the other case (the one that directs me to computer.org).
	I corrected the wrong one in ieee and filled the missing one. 

	Later on, I merged the two author datasets. After merging, I compared this merged dataset
	witht DBLP data from Vispubdata. I found that four papers' authors data were incorrect in my merged data. 
	I corrected my data. The next step is to fill in author affiliation data. 

	At this step, the author df has 181 rows where IEEE Author Affiliation is missing. I manually entered/updated 
	some of the missing data (and even some existing data): affiliation name, country origin, affiliation type, 
	and sometimes author names in both IEEE and OpenAlex data. Note that in this process, for 15 authors, I need to 
	send emails to know their affiliations. 

	After this step, there are still 86 rows where IEEE Author Affiliation is missing. 
	Luckily, among these 86 rows, 68 rows have author data from openalex. I manually checked the openalex author data
	for these 66 rows. I checked the data agains the source PDFs. Only three authors/rows have minor errors. 
	I corrected these errors and later in this scripe I filled in the missing IEEE Author Affiliation 
	with OpenAlex's Raw Affiliation String and named that column as IEEE Author Affiliation Filled

	There are 20 rows where both IEEE and openalex miss information. I manually entered the data. 

	After that, I corrected some errors in OpenAlex, changed affiliation type to binary types, 
	and did some checking. 
"""

import sys
import pandas as pd
import re
import numpy as np
import csv
import difflib 

IEEE_AUTHOR = sys.argv[1]
OPENALEX_AUTHOR = sys.argv[2]
PAPERS_TO_STUDY = sys.argv[3]
VISPUBDATA = sys.argv[4]
MERGED_AUTHOR_DF = sys.argv[5]

def get_dicts(VISPUBDATA):
	# get year_dict and title_dict
	vispd = pd.read_csv(VISPUBDATA)
	dois = vispd.loc[:, "DOI"].tolist()
	titles = vispd.loc[:, "Title"].tolist()
	years = vispd.loc[:, "Year"].tolist()
	doi_year_dict = dict(zip(dois, years))
	doi_title_dict = dict(zip(dois, titles))
	return doi_year_dict, doi_title_dict

def read_txt(INPUT):
	"""read txt files and return a list
	"""
	raw = open(INPUT, "r")
	reader = csv.reader(raw)
	allRows = [row for row in reader]
	data = [i[0] for i in allRows]
	return data

def update_ieee_orig(DF): # df here is iee_orig
	"""update ieee_org

	ieee_org is wrong in '10.1109/TVCG.2008.157' as it contains an additional author that shouldn't be there;
	also, ieee_org lacks author info for '10.1109/VIS.1999.10000'.

	What this function does is to delete the additional author in '10.1109/TVCG.2008.157' and update info in 
	that paper. Then, I added author data manually for '10.1109/VIS.1999.10000'.

	"""
	DF = DF.drop(DF[DF.DOI == '10.1109/VIS.1999.10000'].index)
	row_to_drop = DF.index[DF.DOI == '10.1109/TVCG.2008.157'].tolist()[0]
	df_dropped = DF.drop([row_to_drop])
	df_dropped.loc[df_dropped.DOI == '10.1109/TVCG.2008.157', 'Number of Authors'] -= 1
	df_dropped.loc[df_dropped.DOI == '10.1109/TVCG.2008.157', 'Author Position'] -= 1.0
	df = df_dropped
	FILL_DATA = [
	{
		'Year': 1999,
		'DOI': '10.1109/VIS.1999.10000',
		'Title': 'Progressive Compression of Arbitrary Triangular Meshes',
		'Number of Authors': 3,
		'Author Position': 1,
		'Author Name': 'Daniel Cohen-Or',
		'Author ID': np.NaN,
		'Author Affiliation': 'Tel Aviv University',
		'One Affiliation': True,
	},
	{
		'Year': 1999,
		'DOI': '10.1109/VIS.1999.10000',
		'Title': 'Progressive Compression of Arbitrary Triangular Meshes',
		'Number of Authors': 3,
		'Author Position': 2,
		'Author Name': 'David Levin',
		'Author ID': np.NaN,
		'Author Affiliation': 'Tel Aviv University',
		'One Affiliation': True,
	},
	{
		'Year': 1999,
		'DOI': '10.1109/VIS.1999.10000',
		'Title': 'Progressive Compression of Arbitrary Triangular Meshes',
		'Number of Authors': 3,
		'Author Position': 3,
		'Author Name': 'Offir Remez',
		'Author ID': np.NaN,
		'Author Affiliation': 'Tel Aviv University',
		'One Affiliation': True,
	}
	]
	fill_data_df = pd.DataFrame(FILL_DATA)
	df = df.append(fill_data_df, ignore_index = True)
	return df

def get_diff_dois(IEEE, ALEX): # ieee, alex
	# return a list of DOIs where alex is wrong in Number of Authors
	DOIS = list(set(IEEE.DOI))
	diff_dois = []
	for doi in DOIS:
		ieee_n = IEEE[IEEE.DOI == doi]['Number of Authors'].tolist()[0]
		alex_n = ALEX[ALEX.DOI == doi]['Number of Authors'].tolist()[0]
		if ieee_n != alex_n:
			diff_dois.append(doi)
	return diff_dois 

def get_alex_new(IEEE, ALEX, DIFF_DOIS):
	"""
	For DOIs where alex is wrong in Number of Authors, get correct data from IEEE first
	Drop the rows where alex is wrong from alex, and append the correct ieee data to alex_dropped

	Returns:
		alex_new, where data of Number of Authors is correct
	"""
	df_to_append = IEEE[IEEE.DOI.isin(DIFF_DOIS)].iloc[:, 0:6]
	alex_dropped = ALEX.drop(ALEX[ALEX.DOI.isin(DIFF_DOIS)].index)
	alex_new = alex_dropped.append(df_to_append, ignore_index = True)
	return alex_new

def get_sorted_dfs(IEEE, ALEX_NEW, PAPERS):
	"""sort ieee and alex author df by paper index and author position

	I added a variable 'Paper Index' to both ieee and alex_new. I 
	also added a prefix of 'IEEE ' in ieee. Then I sort the two datasets 
	by 'Paper Index' and 'Author Position'. 

	Returns:
		two dataframes, ieee_sorted, and alex_new_sorted

	"""
	IEEE['Paper Index'] = [PAPERS.index(i) for i in IEEE.DOI.tolist()]
	ALEX_NEW['Paper Index'] = [PAPERS.index(i) for i in ALEX_NEW.DOI.tolist()]
	IEEE = IEEE.add_prefix('IEEE ')
	alex_new_sorted = ALEX_NEW.sort_values(
		by=['Paper Index', 'Author Position'], ).reset_index(drop=True)
	ieee_sorted = IEEE.sort_values(
		by=['IEEE Paper Index', 'IEEE Author Position'], ).reset_index(drop=True)
	return ieee_sorted, alex_new_sorted

def get_concat_df(IEEE, ALEX, PAPERS): # ieee_sorted, alex_sorted
	"""check https://stackoverflow.com/a/13680953 for details
	"""
	fuzzy_match_df_list = []
	mismatch_doi_list = []
	for doi in PAPERS:
		df1 = IEEE[IEEE['IEEE DOI'] == doi]
		df2 = ALEX[ALEX['DOI'] == doi]
		try:
			kwargs = {'IEEE Author Name': 
			df2['Author Name'].apply(
				lambda x: difflib.get_close_matches(
					x, df1['IEEE Author Name'], cutoff=0.6)[0])
			}
		except:
			kwargs = {'IEEE Author Name': df1['IEEE Author Name']}
			mismatch_doi_list.append(doi)
		df2 = df2.assign(**kwargs)
		df = df1.merge(df2, on='IEEE Author Name', how='inner')
		fuzzy_match_df_list.append(df)
	print(f'in {len(mismatch_doi_list)} dois, fuzzy matching was not successful, so I assumed author position in merging')
	df = pd.concat(fuzzy_match_df_list, ignore_index=True)
	return df 

def flatten(t):
	"""convert list of lists to a list of items"""
	"""source: https://stackoverflow.com/a/952952"""
	return [item for sublist in t for item in sublist]

def update_with_vispubdata_author_data(VISPD, DF): # vispd, concat_df
	ieee_wrong = [
	'10.1109/INFVIS.2005.1532150',
	'10.1109/VISUAL.2005.1532819',
	'10.1109/VISUAL.2005.1532794',
	'10.1109/VISUAL.1992.235178',
	]
	correct_author_num = [5, 2, 5, 4]
	correct_author_num_dict = dict(zip(ieee_wrong, correct_author_num))
	vispd_names = VISPD.loc[VISPD.DOI.isin(ieee_wrong), 'AuthorNames-Deduped'].tolist()
	dois = flatten([np.repeat(doi, correct_author_num_dict[doi]) for doi in ieee_wrong])
	years = [doi_year_dict[x] for x in dois]
	titles = [doi_title_dict[x] for x in dois]
	author_names = flatten([x.split(';') for x in vispd_names])
	author_nums = flatten([np.repeat(i, i) for i in correct_author_num])
	author_positions = flatten([range(1, i+1) for i in correct_author_num])
	paper_index = [papers.index(doi) for doi in dois]
	DF_TO_FILL = pd.DataFrame({
		'IEEE DOI': dois,
		'DOI': dois,
		'IEEE Year': years,
		'Year': years,
		'IEEE Title': titles,
		'Title': titles,
		'IEEE Number of Authors': author_nums,
		'IEEE Author Position': author_positions,
		'IEEE Author Name': author_names,
		'Number of Authors': author_nums,
		'Author Position': author_positions,
		'Author Name': author_names,
		'IEEE Paper Index': paper_index,
		'Paper Index': paper_index,
	})
	df_dropped = DF.drop(DF[DF['IEEE DOI'].isin(ieee_wrong)].index)
	df_new = df_dropped.append(DF_TO_FILL, ignore_index=True)
	df_new = df_new.sort_values(
		by=['IEEE Paper Index', 'IEEE Author Position'], ).reset_index(drop=True)
	return df_new

def update_country_code(DF, DOI, NEW_DATA):
	DF.loc[DF['DOI'] == DOI, 'First Institution Country Code By Hand'] = NEW_DATA
	# this is to change openalex author names to be the same as IEEE author names
	# DF.loc[DF['DOI'] == DOI, 'Author Name'] = DF.loc[DF['DOI'] == DOI, 'IEEE Author Name']
	return DF 

def update_country_code_by_raw_string(DF, RAW_STRING, NEW_DATA):
    DF.loc[DF['Raw Affiliation String'] == RAW_STRING, 'First Institution Country Code By Hand'] = NEW_DATA
    return DF 

def update_type(DF, DOI, NEW_DATA):
    DF.loc[DF['DOI'] == DOI, 'First Institution Type By Hand'] = NEW_DATA
    return DF 

def update_type_by_raw_string(DF, RAW_STRING, NEW_DATA):
    DF.loc[DF['Raw Affiliation String'] == RAW_STRING, 'First Institution Type By Hand'] = NEW_DATA
    return DF 

def update_affiliations(DF, DOI, NEW_DATA):
    # update both ieee author affiliation, alex first institution names and raw string
    DF.loc[DF['DOI'] == DOI, 'IEEE Author Affiliation'] = NEW_DATA
    DF.loc[DF['DOI'] == DOI, 'First Institution Name'] = NEW_DATA
    DF.loc[DF['DOI'] == DOI, 'Raw Affiliation String'] = NEW_DATA
    return DF 

def update_author_name(DF, DOI, NEW_DATA):
    DF.loc[DF['DOI'] == DOI, 'IEEE Author Name'] = NEW_DATA
    return DF


def update_concat_df(DF): # DF here is concat_df
	"""Update data for specific DOIs

	Return:
		still concat_df, but updated
	"""
	# '10.1109/VISUAL.1996.568115',
	update_country_code(
		DF, 
		'10.1109/VISUAL.1996.568115',
		['US']*3,
	)
	update_type(
		DF, 
		'10.1109/VISUAL.1996.568115',
		['company']*2 + ['facility'],
	)
	update_affiliations(
		DF, 
		'10.1109/VISUAL.1996.568115',
		['MRJ, Inc']*2 + ['NASA Ames Research Center']
	)
	# '10.1109/VISUAL.2000.885735'
	update_country_code(
		DF, 
		'10.1109/VISUAL.2000.885735',
		np.repeat('NL', 6),
	)
	update_type(
		DF, 
		'10.1109/VISUAL.2000.885735',
		['government']*2 + ['education']*4,
	)
	update_affiliations(
		DF, 
		'10.1109/VISUAL.2000.885735',
		np.append(
			np.repeat(
				'Center for Mathematics and Computer Science, CWI, Amsterdam, Netherlands', 2),
			np.repeat(
				'Swammerdam Inst. for Life Sciences, BioCentrum Amsterdam, Amsterdam, Netherlands', 4)
			)
	)
	# '10.1109/VISUAL.1996.568143',
	update_country_code(
		DF, 
		'10.1109/VISUAL.1996.568143',
		['US']*6,
	)
	update_type(
		DF, 
		'10.1109/VISUAL.1996.568143',
		['education']*6,
	)
	update_affiliations(
		DF, 
		'10.1109/VISUAL.1996.568143',
		['Ohio State University, Columbus, OH, USA']*6
	)
	# '10.1109/VISUAL.1999.809936',
	update_country_code(
		DF, 
		'10.1109/VISUAL.1999.809936',
		['US']*3,
	)
	update_type(
		DF, 
		'10.1109/VISUAL.1999.809936',
		['education']*3,
	)
	update_affiliations(
		DF, 
		'10.1109/VISUAL.1999.809936',
		['Worcester Polytechnic Institute, Worcester, MA, USA']*3
	)
	# '10.1109/INFVIS.2002.1173147',
	# IEEE Xplore got author name wrong
	update_country_code(
		DF, 
		'10.1109/INFVIS.2002.1173147',
		['SE', 'US', 'SE'],
	)
	update_type(
		DF, 
		'10.1109/INFVIS.2002.1173147',
		['education']*3,
	)
	update_affiliations(
		DF, 
		'10.1109/INFVIS.2002.1173147',
		[
			'Dept. of Information Science, Uppsala University, Uppsala, Sweden',
			'Dept. of Psychology, Indiana University, Bloomington, Indiana, USA',
			'Dept. of Information Science, Uppsala University, Uppsala, Sweden',
		]
	)
	update_author_name(
		DF, 
		'10.1109/INFVIS.2002.1173147',
		['M. Lind', 'G.P. Bingham', 'C. Forsell'],
	)
	# '10.1109/VISUAL.1992.235175',
	update_country_code(
		DF, 
		'10.1109/VISUAL.1992.235175',
		['US']*12,
	)
	update_type(
		DF, 
		'10.1109/VISUAL.1992.235175',
		['company']*3 + ['government']*2 + ['education']*6 + ['company']*1
	)
	update_affiliations(
		DF, 
		'10.1109/VISUAL.1992.235175',
		[
			'Unisys Corporation',
			'Sterling Software',
			'Unisys Corporation',
			'U.S. Environmental Protection Agency, United States',
			'U.S. Environmental Protection Agency',
			'University of Alabama in Huntsville (UAH), United States',
			'Florida State University, United States',
			'Florida State University, United States',
			'University of Wisconsin, Madison, WI, United States',
			'University of Wisconsin, Madison, WI, United States',
			'University of Wisconsin, Madison, WI, United States',
			'IBM T.J. Watson Research Center, United States',
		]
	)
	# '10.1109/TVCG.2006.182',
	update_country_code(
		DF, 
		'10.1109/TVCG.2006.182',
		['US']*5,
	)
	update_type(
		DF, 
		'10.1109/TVCG.2006.182',
		['education']*5,
	)
	update_affiliations(
		DF, 
		'10.1109/TVCG.2006.182',
		['Brown University, United States']*5,
	)
	# '10.1109/TVCG.2015.2467971',
	update_country_code(
		DF, 
		'10.1109/TVCG.2015.2467971',
		['US']*5,
	)
	update_type(
		DF, 
		'10.1109/TVCG.2015.2467971',
		['education']*5, 
	)
	update_affiliations(
		DF, 
		'10.1109/TVCG.2015.2467971',
		['University of North Carolina at Charlotte, NC, United States']*5,
	)
	# '10.1109/SciVis.2015.7429489', 
	# author affilitions listed on ieee are all WRONG!!!
	# I found the authors' correct affilition on their ieee author id pages
	update_country_code(
		DF, 
		'10.1109/SciVis.2015.7429489',
		['DE']*5,
	)
	update_type(
		DF, 
		'10.1109/SciVis.2015.7429489',
		['education']*5, 
	)
	update_affiliations(
		DF, 
		'10.1109/SciVis.2015.7429489',
		['Technical University of Munich, Germany']*5,
	)
	# '10.1109/VISUAL.2005.1532821',
	update_country_code(
		DF, 
		'10.1109/VISUAL.2005.1532821',
		['AT', 'HR', 'AT', 'AT', 'US'],
	)
	update_type(
		DF, 
		'10.1109/VISUAL.2005.1532821',
		['company']*4 + ['education']*1 
	)
	update_affiliations(
		DF, 
		'10.1109/VISUAL.2005.1532821',
		['VRVis Research Center Vienna, Austria'] + ['AVL-AST Zagreb, Croatia'] + [
		'VRVis Research Center Vienna, Austria']*2 + ['Virginia Tech']
	)
	# '10.1109/VISUAL.2000.885692',
	update_country_code(
		DF, 
		'10.1109/VISUAL.2000.885692',
		['US']*6,
	)
	update_type(
		DF, 
		'10.1109/VISUAL.2000.885692',
		['education']*6,
	)
	update_affiliations(
		DF, 
		'10.1109/VISUAL.2000.885692',
		['University of Utah, Salt Lake City, UT, USA']*4 + ['Vanderbilt University, USA'] + [
		  'University of Utah, Salt Lake City, UT, USA'],
	)
	# '10.1109/VISUAL.1999.809912',
	update_country_code(
		DF, 
		'10.1109/VISUAL.1999.809912',
		['DE']*4,
	)
	update_type(
		DF, 
		'10.1109/VISUAL.1999.809912',
		['education']*2 + ['healthcare']*2,
	)
	update_affiliations(
		DF, 
		'10.1109/VISUAL.1999.809912',
		['WSUGRIS, University of Tubingen, Tubingen, Germany']*2 + [
		 'Department of Neuroradiology, University Hospital Tubingen, Tubingen, Germany']*2 ,
	)
	# '10.1109/VISUAL.1999.809929',
	update_country_code(
		DF, 
		'10.1109/VISUAL.1999.809929',
		['US']*4,
	)
	update_type(
		DF, 
		'10.1109/VISUAL.1999.809929',
		['company']*4,
	)
	update_affiliations(
		DF, 
		'10.1109/VISUAL.1999.809929',
		['IBM T.J. Watson Research Center, United States']*3 + [
		 'UBS Group AG'] ,
	)
	# '10.1109/VISUAL.1999.809884',
	# In this paper, openalex got country wrong and ieee got some of the affiliation wrong
	update_country_code(
		DF, 
		'10.1109/VISUAL.1999.809884',
		['DE']*5,
	)
	update_type(
		DF, 
		'10.1109/VISUAL.1999.809884',
		['nonprofit']*4 + ['education']*1,
	)
	update_affiliations(
		DF, 
		'10.1109/VISUAL.1999.809884',
		['German National Research Centre for Information Technology, Germany']*4 + [
		 'Department of Physics & Astronomy, University of Heidelberg, Germany'] ,
	)
	# '10.1109/VISUAL.1999.809920',
	# openalex got country wrong
	update_country_code(
		DF, 
		'10.1109/VISUAL.1999.809920',
		['DE']*5,
	)
	# '10.1109/VISUAL.1993.398911',
	# openalex got this paper country wrong for the last two authors
	update_country_code(
		DF, 
		'10.1109/VISUAL.1993.398911',
		['RU']*4 + ['DE']*2,
	)
	# '10.1109/VISUAL.2005.1532816',
	# ieee xplore got author positions and author affiliations wrong
	update_author_name(
		DF, 
		'10.1109/VISUAL.2005.1532816',
		[
			'Gregor Schlosser',
			'J ̈urgen Hesser',
			'Frank Zeilfelder',
			'Christian Rossl',
			'Reinhard Manner',
			'Gunther Nurnberger',
			'Hans-Peter Seidel',
		],
	)
	update_country_code(
		DF, 
		'10.1109/VISUAL.2005.1532816',
		['DE']*7,
	)
	update_type(
		DF, 
		'10.1109/VISUAL.2005.1532816',
		['education']*3 + ['nonprofit']*1 + ['education']*2 + ['nonprofit']*1,
	)
	update_affiliations(
		DF, 
		'10.1109/VISUAL.2005.1532816',
		['ICM, Universitäten Mannheim und Heidelberg, Mannheim, Germany']*2 +
		['Institut für Mathematik, Universität Mannheim, Mannheim, Germany'] +
		['Max Planck Institut für Informatik, Saarbruecken, Germany'] +
		['ICM, Universitäten Mannheim und Heidelberg, Mannheim, Germany'] +
		['Institut für Mathematik, Universität Mannheim, Mannheim, Germany'] +
		['Max Planck Institut für Informatik, Saarbruecken, Germany'],
	)
	# '10.1109/VAST.2016.7883507',
	# This is the paper where i don't have ieee author affilition or openalex raw string,
	# but i have openalex first institution name.
	# Another note: Information on IEEE about the first two authors of this paper is WRONG!
	update_country_code(
		DF, 
		'10.1109/VAST.2016.7883507',
		['DE']*5,
	)
	update_type(
		DF, 
		'10.1109/VAST.2016.7883507',
		['education']*5,
	)
	update_affiliations(
		DF, 
		'10.1109/VAST.2016.7883507',
		['University of Stuttgart, Germany']*5
	)
	# '10.1109/VISUAL.2004.38',
	update_country_code(
		DF, 
		'10.1109/VISUAL.2004.38',
		['CN']*1 + ['US']*3,
	)
	update_type(
		DF, 
		'10.1109/VISUAL.2004.38',
		['education']*3 + ['company']*1,
	)
	update_affiliations(
		DF, 
		'10.1109/VISUAL.2004.38',
		['Zhejiang University, China'] + ['Carnegie Mellon University, United States'] + [
			'Massachusetts Institute Of Technology, United States'] + [
				'Mitsubishi Electric Research Laboratories, United States']
	)
	"""The following are cases where i have raw string, but not type or country code"""
	# '10.1109/TVCG.2006.195',
	update_country_code(
		DF, 
		'10.1109/TVCG.2006.195',
		['NL']*3
	)
	update_type(
		DF, 
		'10.1109/TVCG.2006.195',
		['education']*2 + ['government']*1,
	)
	update_affiliations(
		DF, 
		'10.1109/TVCG.2006.195',
		['Swammerdam Institute for Life Sciences (SILS), University of Amsterdam, Netherlands']*2 + [
			'Center for Mathematics and Computer Science (CWI), Netherlands'
		]*1
	)
	# '10.1109/VISUAL.1996.567752',
	update_country_code(
		DF, 
		'10.1109/VISUAL.1996.567752',
		['US']*3
	)
	update_type(
		DF, 
		'10.1109/VISUAL.1996.567752',
		['company']*3
	)
	update_affiliations(
		DF, 
		'10.1109/VISUAL.1996.567752',
		['GE Corporate Research & Development, United States']*3,
	)
	# '10.1109/VISUAL.1999.809907',
	update_country_code(
		DF, 
		'10.1109/VISUAL.1999.809907',
		['NL']*2
	)
	update_type(
		DF, 
		'10.1109/VISUAL.1999.809907',
		['government']*2
	)
	update_affiliations(
		DF, 
		'10.1109/VISUAL.1999.809907',
		['Center for Mathematics and Computer Science (CWI), Netherlands']*2,
	)
	# '10.1109/VISUAL.2004.88',
	update_country_code(
		DF, 
		'10.1109/VISUAL.2004.88',
		['DE']*2
	)
	update_type(
		DF, 
		'10.1109/VISUAL.2004.88',
		['nonprofit'] + ['education']
	)
	update_affiliations(
		DF, 
		'10.1109/VISUAL.2004.88',
		['Caesar Research Center, Bonn, Germany'] + [
		'Interdisciplinary Center for Scientific Computing, Heidelberg, Germany'],
	)
	# '10.1109/VISUAL.2004.113',
	update_type_by_raw_string(
		DF,
		'DLR Goettingen',
		['government']
	)
	update_country_code_by_raw_string(
		DF,
		'DLR Goettingen',
		'DE'
	)
	# '10.1109/VISUAL.2000.885722',
	update_type_by_raw_string(
		DF,
		'ETH Zentrum, CH - 8092 Switzerland',
		'education'
	)
	update_country_code_by_raw_string(
		DF,
		'ETH Zentrum, CH - 8092 Switzerland',
		'CH'
	)
	# '10.1109/VISUAL.2000.885715',
	update_country_code(
		DF, 
		'10.1109/VISUAL.2000.885715',
		['DE']*3 + ['NL'] + ['DE'] + ['NL']
	)
	update_type(
		DF, 
		'10.1109/VISUAL.2000.885715',
		['education']*6,
	)
	update_affiliations(
		DF, 
		'10.1109/VISUAL.2000.885715',
		['University of Bonn, Bonn, Germany'] * 3 + ['Eindhoven University of Technology'] + [
			'University of Bonn, Bonn, Germany'] + ['Eindhoven University of Technology']
	)
	# '10.1109/VISUAL.2000.885731',
	update_country_code(
		DF, 
		'10.1109/VISUAL.2000.885731',
		['US']*6,
	)
	update_type(
		DF, 
		'10.1109/VISUAL.2000.885731',
		['education']*6,
	)
	update_affiliations(
		DF, 
		'10.1109/VISUAL.2000.885731',
		['Brown University, United States']*6,
	)
	# '10.1109/VISUAL.1996.568133',
	update_country_code(
		DF, 
		'10.1109/VISUAL.1996.568133',
		['US']*7,
	)
	update_type(
		DF, 
		'10.1109/VISUAL.1996.568133',
		['healthcare'] + ['education'] + ['facility']*2 + ['healthcare'] + ['education']*2,
	)
	update_affiliations(
		DF, 
		'10.1109/VISUAL.1996.568133',
		['National Jewish Center for Immunology and Respiratory Medicine, United States'] + [
		'University of New Mexico, United States'] + [
		'Sandia National Laboratories, United States']*2 + [
		'National Jewish Center for Immunology and Respiratory Medicine, United States'] + [
		'State University of New York at Stony Brook, United States'] + [
		'University of New Mexico, United States']
	)
	# '10.1109/VISUAL.2005.1532808',
	update_country_code(
		DF, 
		'10.1109/VISUAL.2005.1532808',
		['DE'],
	)
	update_type(
		DF, 
		'10.1109/VISUAL.2005.1532808',
		['education'],
	)
	update_affiliations(
		DF, 
		'10.1109/VISUAL.2005.1532808',
		['University of Stuttgart']
	)
	# '10.1109/VISUAL.1998.745350',
	update_country_code(
		DF, 
		'10.1109/VISUAL.1998.745350',
		['US']*6,
	)
	update_type(
		DF, 
		'10.1109/VISUAL.1998.745350',
		['facility']*6,
	)
	update_affiliations(
		DF, 
		'10.1109/VISUAL.1998.745350',
		['Naval Reseach Lab, Washington, D.C.']*6
	)
	# '10.1109/VISUAL.2005.1532776',
	update_country_code(
		DF, 
		'10.1109/VISUAL.2005.1532776',
		['US']*7,
	)
	update_type(
		DF, 
		'10.1109/VISUAL.2005.1532776',
		['company']*3 + ['facility']*2 + ['company']*2,
	)
	update_affiliations(
		DF, 
		'10.1109/VISUAL.2005.1532776',
		['Kitware, United States']*3 + [
		'Sandia National Laboratories, United States']*2 + [
		'Simmetrix, United States']*2,
	)
	# '10.1109/VISUAL.1996.568150',
	update_country_code(
		DF, 
		'10.1109/VISUAL.1996.568150',
		['NL']*4,
	)
	update_type(
		DF, 
		'10.1109/VISUAL.1996.568150',
		['nonprofit'] + ['government']*2 + ['education']
	)
	update_affiliations(
		DF, 
		'10.1109/VISUAL.1996.568150',
		['Netherlands Energy Research Foundation, Netherlands'] + [
		'Centre for Mathematics and Computer Science (CWI), Netherlands']*2 + [
		'Vrije Universiteit, Netherlands']
	)
	# '10.1109/VISUAL.1990.146398',
	update_country_code(
		DF, 
		'10.1109/VISUAL.1990.146398',
		['US']*4,
	)
	update_type(
		DF, 
		'10.1109/VISUAL.1990.146398',
		['government'] + ['company']*3 
	)
	update_affiliations(
		DF, 
		'10.1109/VISUAL.1990.146398',
		['NASA Ames Research Center, Moffett Field, CA, USA'] + [
		'Sterling Software, United States'] + [
			'Crossfield Marketing, United States'] + [
			'Crystal River Engineering, Inc., Groveland, CA, USA']
	) 
	# '10.1109/VISUAL.1996.568120',
	update_country_code(
		DF, 
		'10.1109/VISUAL.1996.568120',
		['US']*3,
	)
	update_type(
		DF, 
		'10.1109/VISUAL.1996.568120',
		['education']*3 
	)
	update_affiliations(
		DF, 
		'10.1109/VISUAL.1996.568120',
		['University of Illinois at Chicago, United States'] + [
		'University of Chicago, United States'] + [
			'University of Illinois at Chicago, United States']
	) 
	"""BELOW ARE WHERE I FILL AUTHOR DATA FOR ROWS WHERE DATA WAS FROM VISPUBDATA RAW"""
	# '10.1109/INFVIS.2005.1532150',
	update_country_code(
		DF, 
		'10.1109/INFVIS.2005.1532150',
		['US']*5,
	)
	update_type(
		DF, 
		'10.1109/INFVIS.2005.1532150',
		['education']*5,
	)
	update_affiliations(
		DF, 
		'10.1109/INFVIS.2005.1532150',
		['Stanford University, United States']*5,
	) 
	# '10.1109/VISUAL.2005.1532819',
	update_country_code(
		DF, 
		'10.1109/VISUAL.2005.1532819',
		['CA']*2,
	)
	update_type(
		DF, 
		'10.1109/VISUAL.2005.1532819',
		['education']*2,
	)
	update_affiliations(
		DF, 
		'10.1109/VISUAL.2005.1532819',
		['University of Alberta, Canada']*2,
	) 
	# '10.1109/VISUAL.2005.1532794',
	update_country_code(
		DF, 
		'10.1109/VISUAL.2005.1532794',
		['US']*5,
	)
	update_type(
		DF, 
		'10.1109/VISUAL.2005.1532794',
		['facility'] + ['education']*3 + ['facility'],
	)
	update_affiliations(
		DF, 
		'10.1109/VISUAL.2005.1532794',
		['Oak Ridge National Lab, United States'] + [
			'The University of Tennessee, United States']*3 + [
			'Oak Ridge National Lab, United States'],
	) 
	# '10.1109/VISUAL.1992.235178',
	update_country_code(
		DF, 
		'10.1109/VISUAL.1992.235178',
		['US']*4,
	)
	update_type(
		DF, 
		'10.1109/VISUAL.1992.235178',
		['education']*4,
	)
	update_affiliations(
		DF, 
		'10.1109/VISUAL.1992.235178',
		['University of Utah, United States']*4,
	) 
	## IEEE Website updates the name of Sehi LYi but this update is 
	## different from the name shown on PDF. I changed it back. 
	# '10.1109/TVCG.2021.3114876',
	update_author_name(
		DF, 
		'10.1109/TVCG.2021.3114876', 
		["Sehi L'Yi", 'Qianwen Wang', 'Fritz Lekschas', 'Nils Gehlenborg'],
	)
	## I found the in this paper, Some authors' affiliations contain two institutions
	update_country_code(
		DF, 
		'10.1109/TVCG.2011.207',
		['DE']*4,
	)
	update_type(
		DF, 
		'10.1109/TVCG.2011.207',
		['company'] + ['education']*1 + ['company']*2,
	)
	update_affiliations(
		DF, 
		'10.1109/TVCG.2011.207',
		['Fraunhofer MEVIS, Germany'] + [
			'Center of Complex Systems and Visualization (CeVis), University of Bremen, Germany']*1 + [
			'Fraunhofer MEVIS, Germany']*2,
	) 
	## I found that in this paper, the first author has two affiliations
	update_country_code(
		DF, 
		'10.1109/INFVIS.2004.1',
		['FR']*3,
	)
	update_type(
		DF, 
		'10.1109/INFVIS.2004.1',
		['education']*1 + ['nonprofit']*1 + ['education']*1
	)
	update_affiliations(
		DF, 
		'10.1109/INFVIS.2004.1',
		['ecole des mines de nantes nantes france'] + ['INRIA']*1 + ['ecole des mines de nantes nantes france'],
	) 

	return DF

def manual_update(DF, DOI, AUTHOR_NAME, COL_TO_CHANGE, TEXT):
	"""This is to manually update errors in rows where ieee author info is nan 
	and where openalex author info is complete
	"""
	DF.loc[(DF['DOI'] == DOI) & (DF['IEEE Author Name'] == AUTHOR_NAME), COL_TO_CHANGE] = TEXT

def manual_update_concat_df(DF): # DF here is concat_df
    manual_update(
        DF,
        '10.1109/VISUAL.1997.663848',
        'R. Machiraju',
        'Raw Affiliation String',
        'Mississippi State University, Mississippi, United States'
    )
    manual_update(
        DF,
        '10.1109/VISUAL.2004.128',
        'E. Parkinson',
        'Raw Affiliation String',
        'VA Tech Hydro Corporation, Swizerland',
    )
    manual_update(
        DF,
        '10.1109/VISUAL.2004.128',
        'E. Parkinson',
        'First Institution Type',
        'company'
    )
    manual_update(
        DF,
        '10.1109/VISUAL.2004.128',
        'E. Parkinson',
        'First Institution Country Code',
        'CH',
    )
    manual_update(
        DF,
        '10.1109/INFVIS.1999.801864',
        'J. Sean',
        'IEEE Author Name',
        'Jeffrey Senn',
    )
    manual_update(
        DF,
        '10.1109/INFVIS.1999.801864',
        'J. Sean',
        'Author Name',
        'Jeffrey Senn',
    )
    manual_update(
        DF,
        '10.1109/TVCG.2019.2934260',
        'Andrew J. Solis',
        'Raw Affiliation String',
        'University of Texas Austin, Texas, United States',
    )
    manual_update(
        DF,
        '10.1109/TVCG.2019.2934260',
        'Andrew J. Solis',
        'First Institution Name',
        'University of Texas Austin',
    )

def get_concat_df_filled(DF): # DF here is concat_df
	""" find out who don't have affilition, and fill the data manually

	Get the subset of concat_df where there does not exist any affiliation name. 
	Then drop this subset from concat_df

	Update this subset's IEEE Author Affiliation with fill_dict, and then append 
	this updated subset to concat_df_dropped

	Returns:
		concat_df_filled, where all authors have at least one affiliation name

	"""
	fill_dict = {
	'K.I. Joy': 'University of California, Davis, United States',
	'H. Pfister': 'Department of Computer Science, State University of New York at Stony Brook, United States',
	'A.J. Kolojechick': 'Carnegie Mellon University，School of Computer Science，Pittsburgh，United States',
	'M. Roth': 'Computer Graphics Research Group, Deptartment of Computer Science, ETH Zurich, Switzerland',
	'P.C. Wong': 'Pacific Northwest National Laboratory, United States',
	'H. Foote': 'Pacific Northwest National Laboratory, United States',
	'W. Strasser': 'Computer Graphics Lab, University of Tubingen, Germany',
	'M. Tuveri': 'Center for Advanced Studies, Research and Development in Sardinia, Cagliari, Italy',
	'N. Fanst': 'Georgia Institute of Technology, United States',
	'Heike Janicke': 'Image and Signal Processing Group at the Universi ̈at Leipzig, Germany',
	'A. Vilanova': 'Institute of Computer Graphics, Vienna University of Technology, Austria',
	'P. Thiansathaporn': 'Department of Physics & Astronomy, University of North Carolina, Chapel Hill, United States',
	'B. Hegedust': 'Institute of Computer Graphics, Vienna University of Technology, Austria',
	'W.C. Flowers': 'Massachusetts Institute of Technology, United States',
	'G. Turk': 'GVU Center, College of Computing, Georgia Institute of Technology, United States',
	'P. Ermest': 'Philips Medical Systems, Best, Netherlands',
	'T. Moller': 'Department Of Computer And Information Science, The Ohio State University, Columbus, Ohio, United States',
	'K. Fostiropoulos': 'German National Research Centre for Information Technology, Germany',
	'F. Sobieczky': 'University of Göttingen, Germany',
	'W. Bertelheimer': 'Bayerische Motoren Werke AG (BMW) Corporation, Germany',
	}
	to_fill_df = DF[(
		DF['IEEE Author Affiliation'].isnull()) & (
		DF['Raw Affiliation String'].isnull()) & (
		DF['First Institution Name'].isnull())
	]
	rows_to_drop = DF.index[(
		DF['IEEE Author Affiliation'].isnull()) & (
		DF['Raw Affiliation String'].isnull()) & (
		DF['First Institution Name'].isnull())
	]
	concat_df_dropped = DF.drop(rows_to_drop)
	if concat_df_dropped.shape[0] + to_fill_df.shape[0] == DF.shape[0]:
		print('concat_df_dropped has correct row numbers')
	else:
		print('concat_df_dropped has incorrect row numbers')
	name_list = to_fill_df['IEEE Author Name'].tolist()
	kwargs = {'IEEE Author Affiliation' : lambda x: [fill_dict[i] for i in name_list]}
	to_fill_df = to_fill_df.assign(**kwargs)
	concat_df_filled = concat_df_dropped.append(
		to_fill_df, ignore_index=True).sort_values(
		by=['IEEE Paper Index', 'IEEE Author Position'], ).reset_index(drop=True)
	return concat_df_filled

def recode_to_edu(DF): # df here is concat_df_filled
	# openalex got these institutions' type wrong. they should be education.
	edu_recode_list = [
		'Paris Diderot University',
		'Paris Descartes University',
		'École Polytechnique Fédérale de Lausanne',
		'Johns Hopkins University School of Medicine'
	]
	DF.loc[
	  DF['First Institution Name'].isin(edu_recode_list), 'First Institution Type'
	] = 'education'
	return DF 

def get_alex_raw_string_correct(DF): # DF here is concat_df_filled
	"""if openalex raw string is wrong, correct/update it with ieee author affliation
	"""
	openalex_raw_string_wrong = [
		'10.1109/VISUAL.1999.809920', 
		'10.1109/VISUAL.1999.809884', 
		'10.1109/VISUAL.1993.398911',
	]
	DF.loc[DF.DOI.isin(openalex_raw_string_wrong), 'Raw Affiliation String'] = DF.loc[
		DF.DOI.isin(openalex_raw_string_wrong)]['IEEE Author Affiliation']
	return DF

def binary_type(row):
	if row['First Institution Type'] == 'education':
		binary_type = 'education'
	elif row['First Institution Type'] in [
		'facility', 'government', 'company', 'healthcare', 'archive', 'nonprofit','other'
	]:
		binary_type = 'non-education'
	else:
		binary_type = np.NaN
	return binary_type

def binary_type_by_hand(row):
	'''This is to transform type handcoded by me to binary type
	'''
	if row['First Institution Type By Hand'] == 'education':
		binary_type = 'education'
	elif row['First Institution Type By Hand'] in [
		'facility', 'government', 'company', 
		'healthcare', 'archive', 'nonprofit', 'other', 
		# just in case I have input these by hand:
		'noneducation', 'non-education'
	]:
		binary_type = 'non-education'
	else:
		binary_type = np.NaN
	return binary_type

def add_binary_type(DF): # DF here is concat_df_filled
	DF['Binary Institution Type'] = DF.apply(binary_type, axis=1)
	DF['Binary Institution Type By Hand'] = DF.apply(binary_type_by_hand, axis=1)
	return DF 

def check_delete_rename(DF): # DF here is concat_df_filled
	# check paper index, author num, and author positions
	if DF['IEEE Paper Index'].tolist() == DF['Paper Index'].tolist():
		print('Two paper index vectors are equal')
	else:
		print('Something wrong with paper index vectors')
	if DF['IEEE Number of Authors'].tolist() == DF['Number of Authors'].tolist():
		print('Two author num vectors are equal')
	else:
		print('Something wrong with author num vectors')
	if DF['IEEE Author Position'].tolist() == DF['Author Position'].tolist():
		print('Two author position vectors are equal')
	else:
		print('Something wrong with author position vectors\
			, but this is expected as it indicates that the fuzzy matching above works.')
	# delete useless columns
	DF.drop(['Year', 'DOI', 'Title', 'IEEE Paper Index', 'Paper Index'], axis=1, inplace=True)
	# add a column called IEEE Author Affiliation Filled. It is bascially the same as 
	# ieee author affiliation. The only difference is that if ieee is nan, 
	# i get the data from openalex raw string
	DF['IEEE Author Affiliation Filled'] = np.where(
		DF['IEEE Author Affiliation'].notnull(),
		DF['IEEE Author Affiliation'],
		DF['Raw Affiliation String'],
	)
	# rename columns
	DF.rename(columns={
		'IEEE Year': 'Year',
		'IEEE DOI': 'DOI',
		'IEEE Title': 'Title',
		'IEEE Author Affiliation': 'IEEE Author Affiliation Updated',
		'First Institution Name': 'First Institution Name Updated',
		'Raw Affiliation String': 'Raw Affiliation String Updated',
		# 'First Institution Type': 'First Institution Type Updated',
		# 'First Institution Country Code': 'First Institution Country Code Updated',
	}, inplace=True)
	return DF

def main():
	ieee = update_ieee_orig(ieee_orig)
	diff_dois = get_diff_dois(ieee, alex)
	alex_new = get_alex_new(ieee, alex, diff_dois)
	ieee_sorted, alex_sorted = get_sorted_dfs(ieee, alex_new, papers)
	concat_df = get_concat_df(ieee_sorted, alex_sorted, papers)
	concat_df = update_with_vispubdata_author_data(vispd, concat_df)
	concat_df = update_concat_df(concat_df)
	manual_update_concat_df(concat_df)
	concat_df_filled = get_concat_df_filled(concat_df)
	concat_df_filled = recode_to_edu(concat_df_filled)
	concat_df_filled = get_alex_raw_string_correct(concat_df_filled)
	concat_df_filled = add_binary_type(concat_df_filled)
	concat_df_filled = check_delete_rename(concat_df_filled)
	return concat_df_filled

if __name__ == '__main__':
	vispd = pd.read_csv(VISPUBDATA)
	doi_year_dict, doi_title_dict = get_dicts(VISPUBDATA)
	ieee_orig = pd.read_csv(IEEE_AUTHOR)
	alex = pd.read_csv(OPENALEX_AUTHOR)
	papers = read_txt(PAPERS_TO_STUDY)
	df = main()
	df.to_csv(MERGED_AUTHOR_DF, index=False)
