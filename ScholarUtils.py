# ScholarUtils.py
# Utilities to manipulate GoogleScholarSearch results.
#
from serpapi import GoogleScholarSearch
import pandas as pd
import re
#!pip install PyYAML
import yaml

# Keep the API Key in an external YAML file. Format is:
#    SERP_API_KEY: 92340184908390218409819aslkjfk13948
# (without the leading hash)

def InitScholar(configFile):
    with open(configFile, 'r') as stream:
        GoogleScholarSearch.SERP_API_KEY=yaml.safe_load(stream)['SERP_API_KEY']
    
def GetPapers( searchParams, maxPapers=200 ):
    # Answers a list of Google Scholar 'organic_result' structures for papers corresponding to the search params passed.
    # E.g. u=GetPapers({"cites": "7379463099867128855"})

    search=GoogleScholarSearch(searchParams.copy()) # Sigh! The class takes ownership of the parameters dict.
    # search.params_dict['lr']='lang_en' # No - Scholar doesn't have the classifications consistent.
    # Clumsy loop, because we don't know the loop invariant until after the first request:
    results=[]
    while len(results) < maxPapers:
        search.params_dict['start']=len(results)
        searchResult = search.get_json()
        if searchResult.get('error'):
            if searchResult['error'] == "Google hasn't returned any results for this query.":
                print('No papers found for {}'.format(searchParams))
                break
            raise Exception(searchResult)
        results += searchResult['organic_results']
        # Three cases: limited by passed in maxPapers; limited by Google's 'Total results' for the query, or it's a single page result:
        maxPapers = min(maxPapers, searchResult['search_information'].get('total_results',len(results)))
        if search.params_dict['start'] == 0: # First request?
            print('Retrieving {} papers for {}'.format(maxPapers, searchParams))
    return results[:maxPapers] # Truncate, else requesting 3 results would return 10.

def GetPaper( searchParams ):
    # Answers the first 'organic_result' paper corresponding to the search params passed.
    # If not found, answers an empty map. Note - might only find the citing paper.
    # E.g. u=GetPaper({"q": "Search string"})

    results=GetPapers( searchParams, 1 )
    return results[0] if results else {}

yearRE=re.compile('(?:198|199|200|201|202)\d') # Matches 1980 through 2029

def YearFor(paper, **args):
    # Look for publication date in the summary or perhaps the paper link:
    # Keyword args:
    #    defaultYear: Year to use if none found.
    defaultYear=args.get('defaultYear', 2022)
    possibleDate=paper['publication_info']['summary'] + paper.get('resources',[{}])[0].get('link','')
    yearsFound=yearRE.findall(possibleDate)
    return int(yearsFound[0] if yearsFound else defaultYear) # Assume recent if not found, and check manually later if necessary.

def NumCitations(paper):
    # Cited_by may be missing, or total may be either None (Google error, probably) or 0.
    return (paper['inline_links']['cited_by']['total'] or 0) if paper['inline_links'].get('cited_by') else 0
    
def HasEnoughCitations(paper, **args):
    # True if the paper has enough citations for inclusion in the survey.
    # Keyword args:
    #    requiredAnnualCount: citations per year required for inclusion.
    #    finalYear: Last full year of survey.
    requiredAnnualCount=args.get('requiredAnnualCount', 8)
    finalYear=args.get('finalYear', 2020)
    year=YearFor(paper)
    citationsRequired=requiredAnnualCount / 2 if year >= finalYear else (finalYear - year) * requiredAnnualCount
    return NumCitations(paper) > citationsRequired

def AuthorsFor(paper):
    # Returns the (possibly truncated) list of  authors.
    #return (', '.join([author['name'] for author in paper['publication_info']['authors']])
    #            if paper['publication_info'].get('authors') else '') # only authors with Google Scholar entries
    return paper['publication_info'].get('summary','').split(' -')[0]

def RelatedRef(paper):
    # Answers the unique reference to get papers related to this one.
    #return re.sub(r'.*q=related:(.*):scholar.google.com/.*', r'\1', paper['inline_links']['related_pages_link'])
    return paper['result_id']
    
def RelatedQuery(id):
    # Query to pass to GetPapers to get the related papers corresponding to the given related ID:
    return {'q': 'related:{}:scholar.google.com/'.format(id)}
    
def WellCitedPapers(paperList, **args):
    # Answers a dataframe of the well-cited papers from paperList
    # Keyword arguments are passed to HasEnoughCitations.
    return  (pd.DataFrame([(paper['inline_links']['cited_by']['cites_id'], NumCitations(paper),
                   YearFor(paper, **args), paper['title'], AuthorsFor(paper), paper.get('link',''),
                   RelatedRef(paper), paper.get('snippet',''))
                         for paper in paperList if HasEnoughCitations(paper, **args)],
                columns=['Key','Citations','Year','Title', 'Authors','Link','Related','Snippet'])
            )
