# Thirty-two Years of IEEE VIS: Authors, Fields of Study and Citations

This repository contains data files and codes (data processing & analysis) for the paper of Thirty-two years of IEEE VIS: Authors, Fields of Study and Citations. 

## Updated Findings

In Fig. 3(d) and 3(e), we showed that the number of citations for VIS from non-VIS papers has been increasing dramatically but we did not analyze the publication venues of these citation papers. We did it later and found that citations coming from *IEEE Transactions on Visualization and Computer Graphics* accounted for 12.4% of all 153,549 citations (undeduplicated). Citations from *Computer Graphics Forum*, HCI venues, PacificVis, and journals in the filed of Visualization such as *Information Visualization* and *Journal of Visualization* are also major sources. This indicate that **the impacts of VIS are mostly confined to visualization and HCI areas**. Detailed results are available at [https://hongtaoh.com/files/top_venues.html](https://hongtaoh.com/files/top_venues.html).

## For recalicability committee:

Please go to the folder of `reproduce` and simply run `bash script.sh`. 

## Table of Contents

- [Structure](https://github.com/hongtaoh/32vis#structure)
- [Important data](https://github.com/hongtaoh/32vis#important-data)
  - [Data dicionaries for public data](https://github.com/hongtaoh/32vis#data-dicionaries-for-public-data)
    - [VIS PAPER 1990-2021](https://github.com/hongtaoh/32vis#vis-paper-1990-2021)
    - [VIS AUTHORS 1990-2021](https://github.com/hongtaoh/32vis#vis-authors-1990-2021)
    - [VIS PAPER CONCEPTS](https://github.com/hongtaoh/32vis#vis-paper-concepts)
    - [Google Scholar Citations](https://github.com/hongtaoh/32vis#google-scholar-citations)
  - [Large data](https://github.com/hongtaoh/32vis#large-data)
- [Dependencies](https://github.com/hongtaoh/32vis#dependencies)
- [Reproducibility](https://github.com/hongtaoh/32vis#reproducibility)
  - [Re-generate data?](https://github.com/hongtaoh/32vis#re-generate-data)
  - [Okay with our current data?](https://github.com/hongtaoh/32vis#okay-with-our-current-data)

## Structure 

This repository consists of four folders:
  1. [`analyses_and_get_figures`](https://github.com/hongtaoh/32vis/tree/master/analyses_and_get_figures) contains Jupyter notebooks that get the reported statistics and figures in the Results section of our paper. 
  2. [`data`](https://github.com/hongtaoh/32vis/tree/master/data) are data files we created and analyzed.
  3. [`results`](https://github.com/hongtaoh/32vis/tree/master/results) are the output figures generated from codes in `analyses_and_get_figures`. Figures in both the paper and the supplementary material are included. 
  4. [`workflow`](https://github.com/hongtaoh/32vis/tree/master/workflow) contains (1) scripts to obtain data, and (2) Jupyter notebooks to validate data. 

`analyses_and_get_figures` and `results` are easy to understand. The most difficult and critical parts are `workflow` and `data`. For detailed data generation & processing procedures, refere to [`workflow`](https://github.com/hongtaoh/32vis/tree/master/workflow). For detailed descriptions of data that were generated and used in the study, refer to the [`data`](https://github.com/hongtaoh/32vis/tree/master/data) folder. 

## Important data

The most important data files in analysis are as follows:

  1. `data/ht_class/ht_cleaned_author_df.csv`
  2. `data/ht_class/ht_cleaned_paper_df.csv`
  3. `data/interim/openalex_author_df.csv`
  4. `data/processed/openalex_concept_df.csv`
  5. `data/processed/large/openalex_citation_concept_df.csv`
  6. `data/processed/large/openalex_reference_concept_df.csv`
  7. `data/processed/openalex_refeernce_concept_df_unique.csv`

### Data dicionaries for public data

We have also made data that might be useful for other researcers working on scientometric analysis available on Google Sheets: https://docs.google.com/spreadsheets/d/1JRo33XurW28bGK_Snplno1dbRLDkSZf1T7JmpjNDvTw/

#### VIS PAPER 1990-2021

- Conference: The conference track of VIS papers. There are four tracks: InfoVis, SciVis, VAST, vis. Since 2021, IEEE VIS no longer distinguishes between conference tracsk and we assigned the term 'VIS' for all papers published in and after 2021
- Year: The year this paper was published
- Title: Paper title as shown on [vispubdata](https://sites.google.com/site/vispubdata/home) and IEEE Xplore (for 2021 IEEEVIS papers)
- DOI: Paper DOI
- PaperType: either 'J' (Journal paper) or 'C' (conference paper). This data is from [vispubdata](https://sites.google.com/site/vispubdata/home). For IEEEVIS 2021 papers, we classified them all as 'J'
- OpenAlex ID: The OpenAlex ID associated with this paper. With an ID, for example, `W3203914472`, you can assess this paper's metadata on OpenAlex through [`https://api.openalex.org/works/W3203914472`](https://api.openalex.org/works/W3203914472)
- Number of References: Number of references as shown on OpenAlex (as of June 2022)
- Number of Concepts: Number of concepts as shown on OpenAlex (as of June 2022)
- Number of Citations: Number of citations as shown on OpenAlex (as of June 2022)
- Number of Authors: Number of authors
- Cross-type Collaboration: Whether a paper involves collaborations among researchers from universities and non-educational affiliations (e.g., companies, facilities, government, healthcare, etc.)
- Cross-country Collaboration: Whether a paper involves collaborations among researchers from different countries or regions
- With US Authors: Whether a paper involves at least one author from the United States 
- Both Cross-type and Cross-country Collaboration: Whether a paper is both a cross-type and a cross-country collaboration paper
- Google Scholar Citation: Citation counts as shown on Google Scholar (as of June 2022)
- Award: Whether a paper is an award-winning paper. Note that we exclude Test of Time awards
- Award Name: If a paper is an award-winning one, what award did it get. BP: Best Paper; HM: Honorable Mention; BCS: Best Case Study
- Award Track: The conference track that presented this paper this award

#### VIS AUTHORS 1990-2021
- Year: The year this paper was published
- DOI: Paper DOI
- Title: Paper title as shown on [vispubdata](https://sites.google.com/site/vispubdata/home) and IEEE Xplore (for 2021 IEEEVIS papers)
- Number of Authors: Number of authors
- Author Position: Author position
- Author Name: Author name
- OpenAlex Author ID: OpenAlex author ID
- Affiliation Name: Author affiliation name
- Affiliation country code: alpha-2 (ISO 3166) country code for affiliations
- Affiliation Type: The type of an affiliation, as defined by [ROR](https://ror.org/)
- Binary Type: The type of an affiliation, either education or non-education

#### VIS PAPER CONCEPTS
- Year: The year this paper was published
- DOI: Paper DOI
- Title: Paper title as shown on [vispubdata](https://sites.google.com/site/vispubdata/home) and IEEE Xplore (for 2021 IEEEVIS papers)
- Number of Concepts: Number of concepts as shown on OpenAlex (as of June 2022)
- Index of Concept: Index of Concept as shown on OpenAlex (as of June 2022)
- Concept: Concept name
- Concept ID: Concept ID on OpenAlex
- Wikidata: Link to Wikidata page of a Concept
- Level: The level of this Concept as defined by OpenAlex. Level 0 indicates root Concepts like Computer Science and Psychology. The larger the number, the more granualr a Concept is. 
- Score: The score assigned to this Concept by OpenAlex. A higher score indicates this Concept is a better representation of a paper. 

#### Google Scholar Citations
- Year: The year this paper was published
- DOI: Paper DOI
- IEEE Title: Paper title as shown on IEEE Xplore (as of June 2022)
- Title on Google Scholar: Paper title as shown on Google Scholar (as of June 2022)
- Citation Link: Link to papers citing a VIS paper on Google Scholar (as of June 2022)
- Citation Counts on Google Scholar: Citation counts on Google Scholar (as of June 2022)

### Large data

The [`large`](https://github.com/hongtaoh/32vis/tree/master/data/processed/large) folder within `data/processed` is empty because GitHub does not allow uploading files larger than 100M. Large files are stored in the repository of [https://osf.io/zkvjm/](https://osf.io/zkvjm/) (OSF Storage -> large). 

## Dependencies 

This project uses `python 3.8` with the following packages:

```
snakemake
pandas
numpy
matplotlib
seaborn
altair
scikit-learn
scipy
plotnine
beautifulsoup4
selenium
urllib3
requests
lxml
```
All packages can be installed with `pip install pkgname`, for example, `pip install scikit-learn`. For `lxml`, use ` conda install -c anaconda lxml`.

`snakemake` is used for the workflow. For details, see my [tutorial on snakemake](https://github.com/hongtaoh/snakemake-tutorial). 

For citation analysis, we also used `R`. See [citation_analysis.R](https://github.com/hongtaoh/32vis/blob/master/analyses_and_get_figures/citation_analysis.R).

For `python`, we recommend `conda` and creating a virtural environment. After installing [anaconda](https://www.anaconda.com/), you can create a virtual environment:

```
conda create --name 32vis python=3.8
conda activate 32vis
```

Then you can install packages with `conda` or `pip`.

You can also use the `environment.yml` and `requirements.yml` but they contain many packages that are not used at all. 

## Reproducibility

Our work is designed to be reproducible. 

### Re-generate data?

If you want to reproduce our work from the very beginning, after installing the necessary packages mentioned above, you can delete all folders in `data` folder except for `raw` and `README.md`. 

Then:

```
conda activate 32vis
cd workflow
snakemake --cores 1
```

This will generate all data again. Please note that:

  1. We obtained data from the API of OpenAlex. However, OpenAlex updates its data every two weeks. This means that the data you will get will different from ours. The degree of differences is a function of time. For example, if you recreate the data ten years from now, our data will be totally different.
  2. To crawl Google Scholar needs human participant due to the reCAPTCHA security checks. 

After all data is obtained, you can run all files in [`analyses_and_get_figures`](https://github.com/hongtaoh/32vis/tree/master/analyses_and_get_figures) to reproduce our results. 

### Okay with our current data?

If you don't plan to re-generate all the data but just want to reproduce results based on data we already had, you can simply run all files in [`analyses_and_get_figures`](https://github.com/hongtaoh/32vis/tree/master/analyses_and_get_figures) directly. 

## Citation

```
@article{hao2022thirty,
  title={Thirty-two Years of IEEE VIS: Authors, Fields of Study and Citations},
  author={Hao, Hongtao and Cui, Yumian and Wang, Zhengxiang and Kim, Yea-Seul},
  journal={IEEE Transactions on Visualization and Computer Graphics},
  year={2022},
  doi={10.1109/TVCG.2022.3209422},
  publisher={IEEE}
}
```
