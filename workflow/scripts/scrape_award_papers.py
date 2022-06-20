'''
This script scrapes all award papers.
'''
import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import sys

# input
IEEE_AUTHOR_DF = sys.argv[1]

# output
AWARD_PAPER_DF = sys.argv[2]


def get_paragraphs(url):
    r = requests.get(url)
    if r.status_code == 200:
        soup = bs(r.text, 'html.parser')
        article = soup.find('article')
        paragraphs = list(article.stripped_strings)
        
    return paragraphs


def rename(x):
    if 'Honorable Mention Awards' in x:
        return 'HM'
    if 'Best Paper Award' in x:
        return 'BP'
    if 'Test of Time Award' in x:
        return 'TT'
    if 'Best Case Study Award' in x:
        return 'BCS'
    raise ValueError("Unknow award:", x)
    

rearranger = lambda x: [x[-1], x[-3], x[-2], x[-4], x[1], x[0]]


def get_parsed_results(years, years_idx, paragraphs):
    results = []
    intervals = zip(years_idx, years_idx[1:] + [len(paragraphs)])
    
    # every loop includes a year's awards
    for idx, (y1, y2) in enumerate(intervals):
        year = years[idx]
        paper_info = [] # initialize a list to store a paper info
        for i in range(y1+1, y2):
            p = paragraphs[i]
        
            if p.endswith(('Awards:', 'Award:')): 
                award = p.replace(':', '')
                award = rename(award)
                continue
        
            if p.endswith("\nDOI:"):
                p = p.replace(".\nDOI:", "").replace("Awarded at: ", '')
            
            if p == "DOI:":
                p = 'Vis'
            
            # every paper info has four lines: author, title, awarded at, DOI
            paper_info.append(p) 
        
            # all DOIs happen to have "/" not used anywhere else
            if '/' in p and paragraphs[i-1].endswith("DOI:"): 
                paper_info.extend([award, year]) # add award type and year
                results.append(paper_info)
                paper_info = []     
                
    return list(map(rearranger, results))


def doi_debug(results):
    df = pd.read_csv(IEEE_AUTHOR_DF)
    dois = df['DOI'].unique().tolist()
    dois_lower = [d.lower() for d in dois]
    
    for idx, res in enumerate(results):        
        if res[1] in dois:
            pass
        elif res[1].lower() in dois_lower:
            i = dois_lower.index(res[1].lower())
            print(res[1] + " has been unified as --> " + dois[i])
            results[idx][1] = dois[i]
        else:
            print(f"DOI: {res[1]} does not exist in {IEEE_AUTHOR_DF}!")
            
    return results



def get_2021_tt_papers():
    url = 'http://ieeevis.org/year/2021/info/awards/test-of-time-awards'
    paragraphs = get_paragraphs(url)
    tracks = ['VAST', 'InfoVis', 'SciVis']
    tracks_idx = [paragraphs.index(a) for a in tracks]
    
    years, years_idx = [], []
    for idx, p in enumerate(paragraphs):
        p = p.replace(":", "")
        if p.isdigit():
            years.append(int(p))
            years_idx.append(idx)
    
    def get_track(year_idx):
        for i in range(-1, -4, -1):
            if year_idx > tracks_idx[i]:
                return tracks[i]
    
    results = []
    award = 'TT'

    for idx, y_idx in enumerate(years_idx):
        year = years[idx]
        title = paragraphs[y_idx+1]
        author = paragraphs[y_idx+2]
        doi = paragraphs[y_idx+4]
        track = get_track(y_idx)
        results.append([year, doi, award, track, title, author])
    return doi_debug(results)


def main():
    url = 'http://ieeevis.org/year/2022/info/history/best-paper-award'
    paragraphs = get_paragraphs(url)
    years = [y for y in range(2021, 1989, -1)]
    years_idx = [paragraphs.index(str(y)) for y in years]
    assert len(years) == len(years_idx)
    results = get_parsed_results(years, years_idx, paragraphs)
    results = doi_debug(results)
    results.extend(get_2021_tt_papers())
    columns = ['Year', 'DOI', 'Award', 'Track', 'Title', 'Author']
    df = pd.DataFrame(results, columns=columns)
    df.to_csv(AWARD_PAPER_DF, index=False)


if __name__ == '__main__':
    main()
