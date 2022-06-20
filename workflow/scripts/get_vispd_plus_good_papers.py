"""This script gets rid of papers of type of 'M' and that one invalid DOI

input: vispubdata_plus

procedure: 
    - get only papers of the type of 'J' or 'C', or papers of 2021
    - remove the one invalid DOI

output: vispd_plus_good_papers

"""

import pandas as pd
import sys

VISPUBDATA_PLUS = sys.argv[1]
VISPD_PLUS_GOOD_PAPERS = sys.argv[2]

def get_vispd_plus_good_papers(INPUT):
    """get the list of good dois
    """
    vispd_plus = pd.read_csv(INPUT)
    jc = ['J', 'C']
    good_papers = vispd_plus[
        (vispd_plus.PaperType.isin(jc)) | (vispd_plus.Year > 2020)
        ]
    dois = good_papers.loc[:, "DOI"].tolist()
    # remove the invalid DOI
    dois.remove('10.0000/00000001')
    return dois

vispd_plus_good_papers = get_vispd_plus_good_papers(VISPUBDATA_PLUS)

with open(VISPD_PLUS_GOOD_PAPERS, 'w') as f:
    for doi in vispd_plus_good_papers:
        f.write("%s\n" % doi)

