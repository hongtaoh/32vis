# 32 years of IEEE Vis: Authors, Fields of Study and Citations

This repository contains data files and codes (data processing & analysis) for the paper of Thirty-two years of IEEE VIS: Authors, Fields of Study and Citations. 

## Table of Contents

- [Structure](https://github.com/hongtaoh/32vis#structure)
- [Important data](https://github.com/hongtaoh/32vis#important-data)
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


## Dependencies 

This project uses `python 3.8` with the following packages:

```
snakemake
pandas
numpy
matplitlib
seaborn
altair
scikit-learn
scipy
plotnine
beautifulsoup4
selenium
urllib3
requests
```
All packages can be installed with `pip install pkgname`, for example, `pip install scikit-learn`. Note that to install `snakemake`, you need also `pip3 install "git+https://github.com/ashwinvis/datrie.git@python3.8-cythonize"`. `snakemake` is used in this project to control the workflow. For details, see my [tutorial on snakemake](https://github.com/hongtaoh/snakemake-tutorial). 

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
conda activate 31vis
cd workflow
snakemake --cores 1
```

This will generate all data again. Please note that 
  1. We obtained data from the API of OpenAlex. However, OpenAlex updates its data every two weeks. This means that the data you will get will different from ours. The degree of differences is a function of time. For example, if you recreate the data ten years from now, our data will be totally different.
  2. To crawl Google Scholar needs human participant due to the reCAPTCHA security checks. 

After all data is obtained, you can run all files in [`analyses_and_get_figures`](https://github.com/hongtaoh/32vis/tree/master/analyses_and_get_figures) to reproduce our results. 

### Okay with our current data?

If you don't plan to re-generate all the data but just want to reproduce results based on data we already had, you can simply run all files in [`analyses_and_get_figures`](https://github.com/hongtaoh/32vis/tree/master/analyses_and_get_figures) directly. 


