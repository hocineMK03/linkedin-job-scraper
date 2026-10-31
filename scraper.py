import argparse
import random
import re
import time
from datetime import datetime

import pandas as pd
import requests
from bs4 import BeautifulSoup

SEARCH_URL = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"
JOB_URL = "https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{}"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


def parse_args():
    parser = argparse.ArgumentParser(description="Scrape latest LinkedIn jobs")
    parser.add_argument("keywords", nargs="+", help="search keywords")
    parser.add_argument("--location", default="Algeria")
    parser.add_argument("--hours", type=int, default=24)
    parser.add_argument("--max", type=int, default=100)
    return parser.parse_args()


def sleep_a_bit(low=3, high=6):
    time.sleep(random.uniform(low, high))


def get_with_retry(url, params=None, retries=3):
    """GET with handling for network errors and 429. Returns response or None."""
    for attempt in range(retries):
        try:
            response = requests.get(url, params=params, headers=HEADERS, timeout=15)
        except requests.RequestException as e:
            print(f"  request error: {e}, retrying...")
            time.sleep(10)
            continue

        if response.status_code == 429:
            wait = 60 * (attempt + 1)
            print(f"  429 throttled, sleeping {wait}s...")
            time.sleep(wait)
            continue

        return response
    return None


def text_or_empty(el):
    return el.get_text(strip=True) if el else ""


def parse_cards(html):
    soup = BeautifulSoup(html, "html.parser")
    jobs = []

    for li in soup.select("li"):
        div = li.find("div", class_="base-card")
        if not div or not div.get("data-entity-urn"):
            continue

        job_id = div["data-entity-urn"].split(":")[-1]
        jobs.append({
            "id": job_id,
            "title": text_or_empty(div.select_one("h3.base-search-card__title")),
            "company": text_or_empty(div.select_one("h4.base-search-card__subtitle")),
            "location": text_or_empty(div.select_one("span.job-search-card__location")),
            "link": f"https://www.linkedin.com/jobs/view/{job_id}",
        })

    return jobs


def search_jobs(query, location, hours, max_jobs):
    seen = set()
    results = []
    start = 0

    while len(results) < max_jobs:
        params = {
            "keywords": query,
            "location": location,
            "f_TPR": f"r{hours * 3600}",
            "start": start,
        }
        response = get_with_retry(SEARCH_URL, params=params)

        if response is None or response.status_code != 200:
            print("  stopping search (no valid response)")
            break

        cards = parse_cards(response.text)
        if not cards:
            print("  no more results")
            break

        for job in cards:
            if job["id"] not in seen:
                seen.add(job["id"])
                results.append(job)

        print(f"{len(results)} jobs so far...")
        start += len(cards)
        sleep_a_bit()

    return results[:max_jobs]


def fetch_description(job_id):
    response = get_with_retry(JOB_URL.format(job_id))
    if response is None or response.status_code != 200:
        return ""

    soup = BeautifulSoup(response.text, "html.parser")
    el = soup.select_one("div.show-more-less-html__markup")
    return el.get_text("\n", strip=True) if el else ""


def save_excel(jobs, keywords):
    name = re.sub(r"[^\w-]", "", "_".join(keywords))
    filename = f"jobs_{name}_{datetime.now():%Y-%m-%d_%H%M}.xlsx"

    df = pd.DataFrame(jobs, columns=["title", "company", "location", "link", "description"])
    # Excel cells max out at 32767 chars
    df["description"] = df["description"].str.slice(0, 32000)
    df.to_excel(filename, index=False)
    print(f"saved {len(df)} jobs -> {filename}")


def main():
    args = parse_args()
    query = " ".join(args.keywords)
    print(f"searching: '{query}' in {args.location}, last {args.hours}h, max {args.max}")

    jobs = search_jobs(query, args.location, args.hours, args.max)
    print(f"found {len(jobs)} jobs, fetching descriptions...")

    try:
        for i, job in enumerate(jobs, 1):
            job["description"] = fetch_description(job["id"])
            print(f"  [{i}/{len(jobs)}] {job['title']} @ {job['company']}")
            sleep_a_bit(2, 5)
    except KeyboardInterrupt:
        print("\ninterrupted, saving what we have...")

    for job in jobs:
        job.setdefault("description", "")

    if jobs:
        save_excel(jobs, args.keywords)
    else:
        print("nothing to save")


if __name__ == "__main__":
    main()