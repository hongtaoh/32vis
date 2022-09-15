import pandas as pd
import seaborn as sns
import matplotlib
import matplotlib.pyplot as plt
font = {'family' : 'Arial',
        'weight' : 'normal',
        'size'   : 6.5}
matplotlib.rc('font', **font)

df = pd.read_csv('../data/ht_class/ht_cleaned_paper_df.csv')
# Replace True/False to Yes/No
# Snippet: https://stackoverflow.com/a/45196807
bool_cols = df.columns[df.dtypes == 'bool']
df[bool_cols] = df[bool_cols].replace({True: 'Yes', False: 'No'})
df['PaperType'] = df['PaperType'].replace({'J': 'Jor.', 'C': 'Con.'})

# cutoff
cutoff_year = 2020
df = df[df['Year'] <= cutoff_year]

citenum = 'Number of Citations'
gcitenum = 'Citation Counts on Google Scholar'

vars = ['Cross-type Collaboration', 'Cross-country Collaboration',
       'With US Authors', 'Award', 'PaperType']
short_varname_dic = {
    'Cross-type Collaboration':'Cross-type',
    'Cross-country Collaboration':'Cross-country',
    'With US Authors':'W/ US Authors'
}

# generate figure c
# THE FOLLOWING IS FOR THE REPLICABILITY STAMP
smallfontsize = 6
f, axs = plt.subplots(5,1,
                      figsize=(3.5,3.5),
                      sharex=True,
                      sharey=False,
                      gridspec_kw=dict(height_ratios=[1,1,1,1,1]))
g0 = sns.boxplot(x=df[citenum], y=df['Award'].astype(str), palette="Set2", ax=axs[0])
g0 = sns.stripplot(x=df[citenum], y=df['Award'].astype(str), 
              size=2, color="orange", linewidth=0, ax=axs[0], alpha=0.2)
g0.set_xlabel("")
g0.set_ylabel("Awards", fontsize = smallfontsize)
###########
g1 = sns.boxplot(x=df[citenum], 
                 y=df['Cross-type Collaboration'].astype(str), palette="Paired", ax=axs[1])
g1 = sns.stripplot(x=df[citenum], y=df['Cross-type Collaboration'].astype(str), 
              size=2, color="orange", linewidth=0, ax=axs[1], alpha=0.2)
g1.set_xlabel("")
g1.set_ylabel("Cross-Type", fontsize = smallfontsize)
#############
g2 = sns.boxplot(x=df[citenum], 
                 y=df['Cross-country Collaboration'].astype(str), palette="vlag", ax=axs[2])
g2 = sns.stripplot(x=df[citenum], y=df['Cross-country Collaboration'].astype(str),
                   size=2, color="orange", linewidth=0, ax=axs[2], alpha=.2)
g2.set_xlabel("")
g2.set_ylabel("Cross-Country", fontsize = smallfontsize)
################
g3 = sns.boxplot(x=df[citenum], 
                 y=df['With US Authors'].astype(str), 
                 palette="Paired", 
                 ax=axs[3],
                 order = ['No', 'Yes'],  
                )
g3 = sns.stripplot(x=df[citenum], y=df['With US Authors'].astype(str), 
                   order = ['No', 'Yes'], 
              size=2, color="orange", linewidth=0, ax=axs[3], alpha=0.2)
g3.set_xlabel("")
g3.set_ylabel("US Authors", fontsize = smallfontsize)
##################
g4 = sns.boxplot(x=citenum, y='PaperType', data=df, palette="Set2", ax=axs[4])
g4 = sns.stripplot(x=citenum, y='PaperType', data=df,
              size=2, color="orange", linewidth=0, ax=axs[4], alpha=0.2)
g4.set_xlabel('Number of citations', fontsize = 8)
g4.set_xscale("log")
g4.set_ylabel("Paper Type", fontsize = smallfontsize)
f.text(-0.1, 1.05, 'c', transform=g0.transAxes, 
            size=10, weight='bold')
f.savefig('fig-7c.png', dpi=150)

# ## generate figure a, b
# f, axs = plt.subplots(1,2,
#                       figsize=(14,5),
#                       sharex=False,
#                       sharey=False,)

# ##### Percentile
# ## OpenAlex
# cits = df[citenum].sort_values(ascending=False).tolist()
# dff = pd.DataFrame(cits, columns = ['citations'])
# dff['pdf'] = dff['citations'] / sum(dff['citations'])
# dff['cdf'] = dff['pdf'].cumsum()
# dff['ccdf'] = 1 - dff['cdf']
# dff = dff.reset_index()
# dff['rank'] = (dff['index'] + 1)/dff.shape[0]
# g2 = dff.plot(x = 'rank', y = 'cdf', grid=True, label='OpenAlex', ax=axs[0])
# # g2.set_xlabel('Paper percentile by citations (from high to low)')
# g2.set_ylabel('Cumulative citation share')

# ### Google Scholar
# cits = df[gcitenum].dropna().sort_values(ascending=False).tolist()
# dff = pd.DataFrame(cits, columns = ['citations'])
# dff['pdf'] = dff['citations'] / sum(dff['citations'])
# dff['cdf'] = dff['pdf'].cumsum()
# dff['ccdf'] = 1 - dff['cdf']
# dff = dff.reset_index()
# dff['rank'] = (dff['index'] + 1)/dff.shape[0]
# g2_2 = dff.plot(x = 'rank', y = 'cdf', grid=True, ax = g2, label='Google Scholar')
# g2_2.set_xlabel('Paper rank')
# g2_2.text(-0.1, 1.05, 'a', transform=g2_2.transAxes, 
#             size=25, weight='bold')

# ###### Conference tracks
# g3 = sns.violinplot(x='Conference', y=citenum, data = df, palette="Set2", ax=axs[1])
# g3.set_yscale("log")
# g3.set_xlabel('Conference track')
# g3.text(-0.1, 1.05, 'b', transform=g3.transAxes, 
#             size=25, weight='bold')

# ##### Save fig
# f.savefig('fig7-a-b.png', dpi=150)
