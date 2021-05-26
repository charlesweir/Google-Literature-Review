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
    
def GetPapers( searchParams ):
    # Answers a list of Google Scholar 'organic_result' structures for papers corresponding to the search params passed.
    # E.g. u=GetPapers({"cites": "7379463099867128855"})

    search=GoogleScholarSearch(searchParams.copy()) # Sigh! The class takes ownership of the parameters dict.
    # search.params_dict['lr']='lang_en' # No - Scholar doesn't have the classifications consistent.
    firstPage=search.get_json()
    if (firstPage.get('error')):
        if firstPage['error'] == "Google hasn't returned any results for this query.":
            return []
        raise Exception(firstPage['error'])
    numResults = firstPage['search_information'].get('total_results',
                                 len(firstPage['organic_results'])) # Missing total_results means 1 paper.
    if numResults > 1000: raise Exception('Too many results: {} for {}'.format(numResults, searchParams))
    print('Retrieving {} papers for {}'.format(numResults, searchParams))
    results=firstPage['organic_results']
    for i in range(10, numResults, 10):
        search.params_dict['start']=i
        results += search.get_json()['organic_results']
    return results

def GetPaper( searchParams ):
    # Answers the first 'organic_result' paper corresponding to the search params passed.
    # If not found, answers an empty map. Note - might only find the citing paper.
    # E.g. u=GetPaper({"q": "Search string"})

    print('GetPaper:{}'.format(searchParams))
    search=GoogleScholarSearch(searchParams.copy()) # Sigh! The class takes ownership of the parameters dict.
    #search.params_dict['lr']='lang_en' # No! This causes Scholar to miss some papers.
    firstPage=search.get_json()
    if (firstPage.get('error')):
        if firstPage['error'] == "Google hasn't returned any results for this query.":
            return {}
        raise Exception(firstPage['error'])
    results=firstPage.get('organic_results',[{}])
    return results[0]

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
