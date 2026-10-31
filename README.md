# LinkedIn Jobs Scraper

A small Python script that finds the latest LinkedIn jobs for any keywords and saves them in an Excel file. You give it keywords, it gives you a file with the job title, company, location, link and full description.

It is free and open source. You do not need a LinkedIn account. You do not need an API key.

## What it does

1. You run the script with some keywords, for example `frontend react`.
2. The script searches the public LinkedIn job pages.
3. It collects the jobs from the newest results, page after page, until it reaches the number you want.
4. It opens each job to read the full description.
5. It saves everything in an Excel file in the folder where you run it.

The script waits a few seconds between requests. This is on purpose. It makes the script slower, but it helps you avoid being blocked.

## Requirements

* Python 3.9 or newer
* An internet connection

## Installation

First, download the project and open a terminal in the project folder.

Create a virtual environment. This keeps the project libraries separate from the rest of your computer.

```
python -m venv venv
```

Activate it.

On Windows (PowerShell or cmd):

```
venv\Scripts\activate
```

On Linux or macOS:

```
source venv/bin/activate
```

Install the libraries:

```
pip install requests beautifulsoup4 pandas openpyxl
```

## How to use it

The basic command is:

```
python scraper.py KEYWORDS
```

Everything you write after `scraper.py` that is not an option is used as the search keywords.

Examples:

```
python scraper.py frontend react
python scraper.py fullstack developer
python scraper.py data analyst --location Algiers
python scraper.py python --hours 72 --max 50
```

## Options

**keywords** (required)
One or more words to search for. You do not need quotes. `frontend react` is the same as "frontend react".

**--location**
The place to search in. The default is `Algeria`. You can use a country or a city, for example `Algiers`, `Germany` or `France`.

**--hours**
Only show jobs posted in the last number of hours. The default is `24`. Use `72` for three days or `168` for one week.

**--max**
The maximum number of jobs to collect. The default is `100`.

## Example run

```
python scraper.py frontend react --max 100
```

You will see messages like this:

```
searching: 'frontend react' in Italy, last 24h, max 100
25 jobs so far...
50 jobs so far...
found 50 jobs, fetching descriptions...
  [1/50] Frontend Developer @ Example Company
  ...
saved 50 jobs -> jobs_frontend_react_2026-10-31_1430.xlsx
```

## The Excel file

The file name has your keywords and the date and time, so you never overwrite an old file.

The columns are:

1. title
2. company
3. location
4. link
5. description

Excel cells can hold about 32,000 characters. Very long descriptions are cut at that limit.

## How it works inside

This part is for people who want to understand or change the code.

**Step 1: Searching.**
LinkedIn has a public "guest" address that returns job cards as simple HTML. The script sends a request with your keywords, location and time filter. The `start` value moves through the pages: 0, then 25, then 50, and so on. The script adds the number of cards it really received, because pages do not always have exactly 25 jobs.

**Step 2: Reading the cards.**
The script uses BeautifulSoup to read the HTML. For each card it takes the job ID, title, company, location and link. It saves the job IDs in a set, so the same job is never added twice.

**Step 3: Reading the descriptions.**
For each job ID, the script opens a second public address and reads the description text.

**Step 4: Waiting.**
After every request the script sleeps for a random time, 3 to 6 seconds for searches and 2 to 5 seconds for descriptions. A random time looks more natural than a fixed one.

**Step 5: Errors.**
If LinkedIn answers with error 429, it means "too many requests". The script waits 60 seconds, then 120, then 180, and tries again. After three tries it stops and keeps the jobs it already has.

**Step 6: Saving.**
Pandas puts the jobs in a table and writes the Excel file. If you press Ctrl+C while the descriptions are loading, the script still saves the jobs it finished.

## Main functions

* `parse_args()` reads the command line options.
* `get_with_retry()` sends a request and handles network errors and error 429.
* `parse_cards()` turns search page HTML into a list of jobs.
* `search_jobs()` loops through the pages until it has enough jobs.
* `fetch_description()` gets the description of one job.
* `save_excel()` writes the Excel file.
* `main()` connects all the steps.

## Run it from anywhere

You can call the script from any folder, without activating the virtual environment.

On Windows, create a file called `scrape.bat` in a folder that is in your PATH:

```
@echo off
C:\full\path\to\project\venv\Scripts\python.exe C:\full\path\to\project\scraper.py %*
```

Then you can write:

```
scrape frontend react
```

On Linux or macOS, add an alias to your `~/.bashrc` or `~/.zshrc`:

```
alias scrape='/full/path/to/project/venv/bin/python /full/path/to/project/scraper.py'
```

Open a new terminal, and the `scrape` command is ready.

## Tips

1. Use a narrow search. LinkedIn gives about 1000 results at most for one search, and old results are not always useful.
2. If you get fewer jobs than you asked for, there are not enough new jobs. Try `--hours 72` or broader keywords.
3. Run the script one or two times a day, not all the time.
4. Do not lower the sleep times. Fast scraping gets your IP address blocked.

## Common problems

**I get status 429 or the script stops early.**
LinkedIn is limiting you. Wait 15 to 30 minutes, then try again with a smaller `--max`.

**The descriptions are empty.**
The page may have been throttled, or LinkedIn changed its HTML. Open one job page address, look at the HTML, and update the selector `div.show-more-less-html__markup` in `fetch_description()`.

**The script finds 0 jobs.**
Check your spelling and location. Also check that LinkedIn did not change the card HTML. The selectors in `parse_cards()` may need an update.

**PermissionError when saving the Excel file.**
The file is open in Excel. Close it and run the script again.

## Important notice

This project is for personal and educational use. Scraping LinkedIn is against the LinkedIn Terms of Service. Use the script at your own risk, with low volume, and do not log in with your real account. The author is not responsible for how you use it. If you need a stable and fully allowed way to get job data, look at official job APIs.

LinkedIn can change its pages at any time. When that happens, the script may stop working until the selectors are updated.

## Contributing

Contributions are welcome. You can open an issue to report a bug or suggest an idea. You can also send a pull request. Good ideas for new features:

1. Save the results to CSV or JSON
2. Filter by experience level or job type
3. Skip jobs that were already saved in a previous run
4. Send a daily email with the new jobs

## License

This project uses the MIT License. You can use it, copy it, change it and share it for free.