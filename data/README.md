# Data

## 1. Raw

### `vispubdata.csv`

Taken from https://docs.google.com/spreadsheets/d/1xgoOPu28dQSSGPIp_HHQs0uvvcyLNdkMF9XtRajhhxU/edit

## 2. Interim

### Checking

data files in this subfolder is to make sure the papers I identified on OpenAlex correctly correspond to actual VIS papers. 

#### `title_query_empty_doi_query_404_1.txt`, `title_query_404_1.txt`

These are the outputs of `get_vispd_openalex_match_1.py`. 

#### `title_query_404_2.txt`, `doi_query_404_2.txt`, `title_query_empty_doi_query_404_2.txt`

These are the output of `get_vispd_openalex_match_2.py`.

#### `title_query_empty_doi_query_404_dfs.txt`, `title_query_404_dfs.txt`, `doi_query_404_dfs.txt`

These are the output of `get_openalex_dfs.py`

### methods_reporting

data files in this folder contains data I need to report statistics in the Methods section. 

#### `crossref.csv`

I queried VIS paper DOIs on Crossref API and obtained the reference counts and first author affilations.

#### `ieee_citation_metrics.csv`

I randomly selected 100 VIS papers and obtained their citation counts (on Crossref, Scopus, and Web of Science) as displayed on IEEE Xplore 

#### `wod_id.csv`

I queried VIS papers on Web of Science by DOI and created a table containing a paper's DOI and its corresponding Web of Science ID. What I want to do is to see how many VIS papers can be identified via DOI query on Web of Science. 

### `vispd_openalex_match_1.csv`, `vispd_openalex_match_2.csv`, `openalex_author_df.csv`

These are outputs of `get_vispd_openalex_match_1.py`, `get_vispd_openalex_match_2.py`, and `get_openalex_dfs.py`.

### `ieee_author_df.csv`

This is author data scraped from IEEE Xplore. 

### `award_paper_df.csv`

This is data on award-winning VIS papers.  

## 3. Processed

### `titles_2021.csv`

paper titles for IEEE VIS 2021. 

### `dois_2021.csv`

DOIS for IEEE VIS 2021 papers. 

### `vispubdata_plus.csv`

I appended data of IEEE VIS 2021 to the raw dataset of `vispubdata.csv` which contains data for papers published in 1990-2020. 

### `vispd_plus_good_papers.txt`

This contains a list of paper DOIs. I excluded papers with paper type of "M" and that invalid DOI ('10.0000/00000001') in `VISPUBDATA_PLUS.csv`.

### `papers_to_study.txt`

This is a list of DOIs. This list is **very important** because it contains the DOIs for papers we will include in the analysis of the present study. 

`papers_to_study.txt` is different from `vispd_plus_good_papers.txt` because it excludes the nine papers inaccessible in OpenAlex. 

### `openalex_paper_df.csv`, `openalex_author_df.csv`, `openalex_reference_df.csv`, `openalex_concept_df.csv`

These four datasets are the outputs of `get_openalex_dfs.py`. They contain data for papers included in `papers_to_study.txt`. The four datasets are about paper meta info, author info, reference lists, and field of study, respectively. 

### `large` folder

The large folder contains four large datasets:

  1. `openalex_citation_author_df.csv`
  2. `openalex_citation_concept_df.csv`
  3. `openalex_reference_author_df.csv`
  4. `openalex_reference_concept_df.csv`

These data are about author and concepts in VIS's cited (i.e., references) and citing papers (i.e., those who were citing VIS). 

### `openalex_reference_paper_df.csv`

This is basically the same as those in `large` folder. I put it `processed` directly because it is below 50M and could be uploaded to GitHub directly. 

### `openalex_reference_author_df_unique.csv`, `openalex_reference_concept_df_unique.csv`, `openalex_reference_paper_df_unique.csv`

These are about author, concept, and paper metadata for VIS's cited papers. I added the word "unique" because there are no duplicated cited papers in these three files. In, for example, `openalex_reference_author_df.csv`, there are duplicated cited papers because one cited paper might be cited by many different VIS papers. 

### `ieee_paper_df.csv`

This is paper metadata of VIS papers scraped from IEEE Xplore. 

### `gscholar_data.csv`

This is citation data of VIS papers scraped from Google Scholar.

### `merged_author_df.csv`

I merged author `ieee_author_df.csv` and `openalex_author_df`, compared the merged with Vispubdata, corrected incorrect information, and manually filled in missing author affiliation information. 

## 4. ht_class

### `merged_aff_type_predicted.csv` and `merged_country_predicted.csv`

These are the outputs of applying classifiers to merged author dataset. 

### `ht_cleaned_author_df.csv` and `ht_cleaned_paper_df.csv`

These two are the cleaned version of author and paper datasets. 

## 5. plots

  - `author cord` contains data for [Cross Country Collaboration Chord Diagram](https://observablehq.com/@hongtaoh/chord-speed-diagram)

  - `top_concepts_trends_df.csv` is data for [Concepts popularity trends tiny charts](https://observablehq.com/@hongtaoh/concepts-popularity-trends-tiny-charts)

  - `sankey` contains data for [Sankey diagram of citation flows](https://observablehq.com/@hongtaoh/sankey-diagram-of-citation-flows)

  - `cooccurance` contains data for [IEEE VIS paper concepts cooccurance chord diagram](https://observablehq.com/@hongtaoh/ieee-vis-paper-concepts-cooccurance-chord-diagram)
