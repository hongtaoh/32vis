# 32 years of IEEE Vis

This repository contains data files and codes (data processing & analysis) for the paper of Thirty-two years of IEEE VIS. 

## Structure 

This repository consists of four folders:
  1. `analyses_and_get_figures` contains Jupyter notebooks that get the reported statistics and figures in the Results section of our paper. 
  2. `data` are data files we created and analyzed.
  3. `results` are the output figures generated from codes in `analyses_and_get_figures`. Figures in both the paper and the supplementary material are included here. 
  4. `workflow` contains (1) scripts to obtain data, and (2) Jupyter notebooks to validate data. 

`analyses_and_get_figures` and `results` are easy to understand. The most difficult and critical parts are `workflow` and `data`. For detailed data generation & processing procedures, refere to the README of the `workflow` folder. For detailed descriptions of data we generated, refer to the README of the `data` folder. 

The most important data files in analysis are as follows:

  1. `data/ht_class/ht_cleaned_author_df.csv`
  2. `data/ht_class/ht_cleaned_paper_df.csv`
  3. `data/interim/openalex_author_df.csv`
  4. `data/processed/openalex_concept_df.csv`
  5. `data/processed/large/openalex_citation_concept_df.csv`
  6. `data/processed/large/openalex_reference_concept_df.csv`
  7. `data/processed/openalex_refeernce_concept_df_unique.csv`


