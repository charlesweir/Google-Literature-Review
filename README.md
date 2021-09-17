# DCS-Literature-Review

This project contains Python code in Jupyter Notebooks used to conduct a systematic literature review using Google Scholar via a SERP API service. 

It simplifies three aspects of literature reviews:
* It creates a spreadsheet with papers, snippets and links to the PDFs ready for fast dual coding
* It remembers which papers have been coded, so avoids repetition.
* It uses what is probably the most complete research database, and uses 'related articles' links. 

The process supports a snowballing approach, starting from some initial papers and exploring 'related articles'. It can be used in two modes, to:
* Find a set of papers satisfying some manually selected criteria, with or without double coding by two authors
* Find a small set of the 'most important' papers satisfying a similar criteria, using citation counts as a mechanical filter, again with or without double coding.

We used an iterative process, and this is reflected in the notebooks: 

* FirstStep.ipynb starts from a few 'seed' papers and creates a first spreadsheet for the reviewers to code from. 
* Snowballing.ipynb takes a coded spreadsheet and generates a list of further papers to assess. It is run several times; each time creating a new 'round' of papers.
* Analysis.ipynb carries out some numeric and graphical analysis on the resulting list of papers. 

More instructions are available in the notebooks themselves.

The file ScholarUtils.py contains a short library of utilities for use with a specific Search Engine Results Page (SERP) API service: serpapi.com. While it is quite easy (and now legal) to scrape Google Scholar directly, SerpAPI avoids the throttling limits of a few requests per minute imposed by Google. The service currently provides a limited trial account.

The service requires an API key in the file APIKey.yaml in the same directory as the notebook files. The format of that file is:

    # Comments with the hash character
    SERP_API_KEY: 92340184908390218409819aslkjfk13948

The notebooks are tested and working at the time of upload. They are suitable for modification for any similar literature review based on Google Scholar. FirstStep.ipynb and Snowballing.ipynb will require obvious and minor changes; Analysis.ipynb has more tailoring to the specific needs of the survey, but is usable for whatever value it may offer.

