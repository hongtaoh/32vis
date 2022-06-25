"""get vispubdata_plus

input: dois_2021, vispubdata

output: vispubdata_plus

"""

import sys
import pandas as pd

DOIS_2021 = sys.argv[1]
VISPUBDATA = sys.argv[2]
VISPUBDATA_PLUS = sys.argv[3]

if __name__ == '__main__':
	dois_2021_df = pd.read_csv(DOIS_2021)
	vispd = pd.read_csv(VISPUBDATA)
	vispd_plus = vispd.append(dois_2021_df, ignore_index=True)
	vispd_plus.to_csv(VISPUBDATA_PLUS, index=False)
