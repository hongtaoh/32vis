# Workflow

The folder contains three main items:

  - `Snakefile`. We use [Snakemake](https://github.com/hongtaoh/snakemake-tutorial) as our workflow to generate and process data. This snakefile is where rules and data directories are stored. 
  - `scripts`. This folder contains all the necessary scripts that we ran to get the data in the `data` folder. 
  - `notebooks`. This folder contains necessary validation notebooks. You'll see why they are needed below. 

In the following, I'll explain how we got the data we had in the `data` folder, step by step, in the hope that everybody can reproduce our results. 

## Steps

### 1. Get raw data

The only raw data we had is [Vispubdata](https://docs.google.com/spreadsheets/u/1/d/1xgoOPu28dQSSGPIp_HHQs0uvvcyLNdkMF9XtRajhhxU/edit?usp=sharing). I downloaded it as a csv file and stored it as `data/raw/vispubdata.csv`. 

### 2. Get titles and dois of VIS 2021 papers

Vispubdata does not contain data for VIS 2021 papers. We had to obtain the data on our own. 

I obtained the titles of VIS 2021 papers using the script of `get_titles_2021.py`. The output of this step is `processed/titles_2021.csv` which contains 170 paper titles. 

Then, I used the script of `get_dois_2021.py` to get the DOIs for the paper titles in `processed/titles_2021.csv` through the API of CrossRef ("habanero"). 22 paper failed to have valid IEEE doi prefix (‘10.1109’). For papers with IEEE DOI Prefix, there are 5 papers whose CrossRef title does not match with the title shown on IEEE VIS 2021. Therefore, there are in total 22 + 5 = 27 papers whose query results are false. For these 27 papers, I manually collected their DOIs from IEEE Xplore. The output file is `processed/dois_2021.csv`. I then merged this file with VISPUBDATA and got `vispubdata_plus.csv` which contains data for VIS papers from 1990 to 2021. 

Note that in this step, I have already validated the match results. How I did it is in the notebook of `01-obtain-2021-paper-doi-from-crossref-and-ieee.ipynb`. For papers whose DOIs contain '10.1109' AND whose CR titles match title I scraped, I didn't inspect them because they are correct results. Then I filtered out papers whose titles do not match AND whose DOI does not contain '10.1109'. For papers whose DOI does not contain '10.1109', it is apparent that they are wrong results. 

### 3. Validating DOIs of VISPUBDATA

I excluded papers with paper type of "M" (posters, keynote files, panels) from my analysis. I found only one invalid DOI ('10.0000/00000001'). I checked the titles and found no duplicates. See `workflow/notebooks/03-inspection-of-dois-of-vispubdata-only-j-and-c.ipynb` for details. 

### 4. Validate DOIs for IEEE VIS 2021 papers

In the notebook of `workflow/04-inspection-of-dois-of-2021-papers.ipynb`, I manually checked the DOIs of IEEE VIS 2021 papers. No strange things found. 

### 6. Getting "vispd plus Good Papers"

I then ran `get_vispd_plus_good_papers.py` to get `vispd_plus_good_papers.txt`. 

What `get_vispd_plus_good_papers.py` does is to exclude papers with paper type of "M" and that SINGLE ONE invalid DOI ('10.0000/00000001') in VISPUBDATA_PLUS. 

### 7. VISPUBDATA-OpenAlex Match-1

For each paper in `vispd_plus_good_papers.txt`, I obtained the associated information on OpenAlex, for example, publication year/data, DOI, URL, Title, Venue id and name, etc. I did it with the script of `get_vispd_openalex_match_1.py`. I employed a combination of title query and doi query.

With the notebook of `workflow/notebooks/05-Checking-no-matching-and-no-result-titles-of_vispd_openalex_match_1.ipynb`, I checked:
  - How many papers are there in `title_query_empty_doi_query_404_1` (i.e., those that cannot be found on openalex via a combination of title and doi query) and how many of them can be identified via title modification (i.e., slightly modify the title to query to get the results in openalex. This is because titles on OpenAlex do not necessarily are exactly the same as those on VISPUBDATA, even when they are exactly the same paper.)
  - For papers with successful query results (no matter whether it's through title query or doi query), are they the same paper on OpenAlex and on VISPUBDATA? I checked this because OpenAlex might return multiple results based on title query. In the script of `get_vispd_openalex_match_1.py`, i only used the first result. 

    Therefore, even for papers with successful query results (i.e., title query has results, or title query unsuccessful but doi query is successful), I need to manually check whether their results are the same papers as those on VISPUBDATA. 

The conclusion of my manual validation is that among 11 papers that do not have results in successful title query (Background: Sometimes OpenAlex will return results in title query but the query result is empty), 4 can be identified through title query on OpenAlex if I modify the title a little bit. 

There are 52 papers whose title queries are successful (and not empty) but whose title AND DOI do not match with the information on VISPUBDATA. I manually checked them. I found that 17 papers are indeed wrong results. Among these 17, except for two papers (HyperLic, Escape maps), 15 can be identified via DOI or using a different index in the title query results (one paper can be identified successfully if I remove the `#` in the title).

In sum, (11-4) + 2 = 9 papers don't exist in the system of OpenAlex. 

### 8. VISPUBDATA-OpenAlex Match-2

Based on the result of VISPUBDATA-OpenAlex Match-1, I created the script of `get_vispd_openalex_match_2.py`. What this script does is the following:

  1. Slighly modify the above mentioned five papers' titles (the four in no_result, and the one with `#` among the 56 paeprs with successful but potentially false results) for title queries using the `replace` function.

  2. I said earlier that in `match_1`, there are 52 papers whose results are successful but potentially wrong. I checked them and found that 17 are indeed mistaken matches. Among these 17, 2 papers just do not exist on OpenAlex. Among the 15 that exist on OpenAlex, two one can be identified if I remove the `#` in title for the purpose of query. Then, there remain 14 papers. Among these, 5 can be idenfied via DOI query, and 9 can be identified if I use a different index in the title query results. TAHT IS WHAT I DID, I FIRST CHECK WHETHER A DOI IS IN `to_query_by_doi`, IF NOT, IT GOES THROUGH THE NORMAL PROCEDURE (TITLE QUERY -> CHECK RESULT COUNT -> DOI QUERY), IF YES, I'LL USE DOI QUERY INSTEAD. ALSO, IN THE NORMAL PROCEDURE, I'LL USE A DIFFERENT RESULT INDEX IF THE DOI IS IN `special_result_index_dict`. 

The output file is `vispd_openalex_match_2.csv`. 

I manaully checked the results of `vispd_openalex_match_2.csv` in the notebook of `workflow/notebooks/06-Checking-no-matching-and-no-result-titles-of_vispd_openalex_match_2.ipynb`. The no_result has 7 papers; those are the papers that simply don't exist in openalex. Then, among papers with successful results but potentially wrong, I saw that only two are indeed wrong matches. And these two are indeed inaccessible on openalex. 

In sum, a totla of 7 + 2 = 9 papers among all the 3283 IEEE VIS papers do not exist on openalex. 

### 9. GET PAPERS_TO_SUTDY

`get_papers_to_study.py`, this step simply removes the nine papers inaccessible in OpenAlex from `vispd_plus_good_papers`. This results in a total of 3,233 DOIs. 

### 10. GET OPENALEX DFS

`get_openalex_dfs.py`, this step is very similar to, and also based on VISPUBDATA-OpenAlex Match-2. What I did in `get_openalex_dfs.py` is to take all the DOIs in `vispd_plus_good_papers.txt` and query them (title, or doi) in OpenAlex. There are four main outputs: paper_df, author_df, reference_df, and concept_df. 

After the script is run and the dfs obtained. I used the notebook of `workflow/notebooks/07-Checking-no-matching-and-no-result-titles-of_openalex_paper_df.ipynb` to check the results. It turns out the results are good. No_matching, no_result, and failed_doi are all empty. I then checked the rows where both the title and DOI do not match with those of VISPUBDATA_PLUS. It turns out, all of them are identical papers. THIS MEANS THAT MY SCRIPT OF `GET_OPENALEX_DFS.PY` has the output I desired. 

### 11. GET CITATION DFs

For every paper that has cited papers in `papers_to_study.txt`, I collected its meta data, author info, and concept info. 

In `openalex_paper_df.csv`, for every paper ("A"), there is a url pointing to data about all the paper that have cited "A". I simply opened this url and collect all the information (paper meta, author, concept, etc.). 

### 12. GET REFERENCE DFs

I then ran `get_openalex_reference_dfs.py` to get all the information (paper meta, author, concept, etc.) on all papers that were cited in 3,274 VIS papers. When I got the citing papers' data, OpenAlex provided an URL that contains all citing papers. However, for cited paper (i.e., reference papers), this is not the case. I had to manually collect all cited papers' info one by one. Since there are many duplicates in cited papers, I first dedupped them and then obtain their information. Then, I merged cited papers' info with `data/processed/openalex_reference_df.csv`. When I generated outputs, I obtain both the full datasets (i.e., VIS-cited pairs) and also the "unique" datasets which only included cited papers' information. 

### 13. Get IEEE author and paper title

`get_ieee_author_and_paper_title.py` is simply to scrape author and paper title information for 3,233 VIS papers. 

### 14. Ger merged author df 

`get_merged_author_df.py`:

In this notebook, I first compared the number of authors in IEEE and OpenAlex. I checked PDFs and confirmed that IEEE was wrong in one case, and missed data in the other case (the one that directs me to computer.org). I corrected the wrong one in ieee and filled the missing one. 

Later on, I merged the two author datasets. After merging, I compared this merged dataset witht DBLP data from Vispubdata. I found that four papers' authors data were incorrect in my merged data. I corrected my data. The next step is to fill in author affiliation data. I found that around 50 authorships miss affiliation info. I manually filled it. While doing that, I manually updated the affiliation name, country origin, affiliation type, and sometimes author names in both IEEE and OpenAlex data. I had to manually collect 15 authors' affiliation. 

After that, I merged the two datasets, and change affiliation type to binary types. 

### 15. Get awards info

`scrape_award_papers.py`, this scripts scrape awards info, specifically, year, doi, award, track, title, and author info. The data source is `http://ieeevis.org/year/2022/info/history/best-paper-award`.

### 16. Get Google Scholar data

`get_gscholar_data.py` obtains citation counts on Google Scholar in early March of 2022. 

### 17. Try to get Web of Science ID for 3,233 VIS papers

`get_wos_id.py`, this step is simply to report statistics in the Methods section of Supplementary Material. I want to see how many VIS papers were readily available on Web of Science through simple DOI query. 

### 18. Get classification models

`CLASS_country.py` and `CLASS_type.py` got classification model with logistic regression for country codes and affiliation types, respectively. 

### 19. Get cleaned author and cleaned paper data 

`get_HT_cleaned_author_df.py` and `get_HT_cleaned_paper_df.py` obtained the cleaned version of author and paper meta data used in our data analyses. 

### 20. Generate data for plots

  - `plot_data_author_chord_diagram_data.py` generates data for [Cross Country Collaboration Chord Diagram](https://observablehq.com/@hongtaoh/chord-speed-diagram)

  - `plot_top_concepts_trends.py` generates data for [Concepts popularity trends tiny charts](https://observablehq.com/@hongtaoh/concepts-popularity-trends-tiny-charts)

  - `plot_sankey_data.py` generates data for [Sankey diagram of citation flows](https://observablehq.com/@hongtaoh/sankey-diagram-of-citation-flows)

  - `plot_vis_concepts_cooccurance_data.py` generates data for [IEEE VIS paper concepts cooccurance chord diagram](https://observablehq.com/@hongtaoh/ieee-vis-paper-concepts-cooccurance-chord-diagram)

