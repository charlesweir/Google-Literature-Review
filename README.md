# DCS-Literature-Review

This project contains Python code in Jupyter Notebooks used to conduct a systematic literature review using Google Scholar via a SERP API service. The review is to find a small set of the 'most important' papers in the field, so uses citation counts as a mechanical filter, along with manual double coding by the authors.

We used an iterative process, and this is reflected in the notebooks: 

* FirstStep.ipynb starts from a few 'seed' papers and creates a first spreadsheet for the reviewers to code from. 
* Snowballing.ipynb takes a coded spreadsheet and generates a list further papers to assess. It is run several times; each time creating a new 'round' of papers.
* Analysis.ipynb carries out some numeric and graphical analysis on the resulting list of papers. 

The file ScholarUtils.py contains a short library of utilities for use with a specific Search Engine Results Page (SERP) API service: serpapi.com. This currently provides a free two-week trial account.

The service requires an API key in the file APIKey.yaml in the same directory as the notebook files. The format of that file is:

    # Comments with the hash character
    SERP_API_KEY: 92340184908390218409819aslkjfk13948

The notebooks are tested and working at the time of upload. They are suitable for modification for any similar literature review based on Google Scholar. FirstStep.ipynb and Snowballing.ipynb will require obvious and minor changes; Analysis has more tailoring to the specific needs of the survey, but is offered for whatever value it may offer.

Charles Weir

Lancaster University.
