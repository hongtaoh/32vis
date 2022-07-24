# 32 years of IEEE Vis: Authors, Fields of Study and Citations

This repository contains data files and codes (data processing & analysis) for the paper of Thirty-two years of IEEE VIS: Authors, Fields of Study and Citations. 

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


## Dependencies 

This project uses `python 3.8` with the following packages:

```
snakemake
pandas
numpy
scikit-learn
beautifulsoup4
selenium
urllib3
requests
```

All packages can be installed with `pip install pkgname`, for example, `pip install scikit-learn`. Note that to install `snakemake`, you need also `pip3 install "git+https://github.com/ashwinvis/datrie.git@python3.8-cythonize"`. `snakemake` is used in this project to control the workflow. For details, see my [tutorial on snakemake](https://github.com/hongtaoh/snakemake-tutorial). 

## Reproducibility


