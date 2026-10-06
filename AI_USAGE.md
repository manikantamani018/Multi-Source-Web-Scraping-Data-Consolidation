# AI Usage

I used ChatGPT during this assignment mainly when I got stuck or wanted to
understand a particular implementation.

Most of the work was done by me, including setting up the project, writing and
running the code, checking the scraped data, fixing errors, and testing the
final output.

Approximate usage:

- My work: 70%
- AI assistance: 30%

## How I Used ChatGPT

I used ChatGPT for a few parts of the development process:

- Understanding the assignment requirements
- Getting ideas for the project structure
- Understanding BeautifulSoup selectors
- Checking pagination logic
- Getting help when I faced Python errors
- Reviewing some validation and duplicate-checking logic
- Getting suggestions for improving the README

I did not directly use the generated code without checking it. I ran the code
myself and changed parts of it when I found issues.

## Some Prompts I Used

- How can I scrape multiple pages using BeautifulSoup?
- How can I find the next page link from HTML?
- How should I handle missing elements while scraping?
- Why am I getting this Python import error?
- How can I remove duplicate records?
- How should I validate the scraped data?

## Changes I Made

While running the project, I made changes based on the errors and results I
got.

For example:

- Fixed the BeautifulSoup installation/import issue.
- Changed the Quotes scraper to keep the actual page URL as the source URL.
- Improved the handling of missing `href` values.
- Checked the pagination by running the scraper against the websites.
- Checked the generated CSV file.
- Checked the summary report.
- Ran the test cases after making the changes.

## Testing

I ran the project locally using:

py main.py

The scraper successfully collected:

- Books to Scrape: 1000 records
- Quotes to Scrape: 100 records

After cleaning and duplicate handling, the final dataset contained 1099
records.

I also ran the test cases using:

py -m pytest -q

## Final Note

ChatGPT was used as a supporting tool during development. I reviewed the
suggestions, ran the code myself, fixed errors, and verified the final
results before completing the assignment.
