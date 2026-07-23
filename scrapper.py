from serpapi import GoogleSearch
import json
import csv
from datetime import date

# Define your target search parameters
params = {
    "engine": "google_jobs",
    "q": "junior accountant OR junior bookkeeper",
    "location": "Canada",
    "hl": "en",
    "api_key": "YOUR_SERPAPI_KEY" # Free tier offers 100 searches/month
}

search = GoogleSearch(params)
results = search.get_dict()
jobs = results.get("jobs_results", [])

# Append summary counts & job details to a daily dataset
today = date.today().isoformat()
print(f"[{today}] Total entry-level postings found: {len(jobs)}")

with open("canada_accounting_jobs.csv", "a", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    for job in jobs:
        writer.writerow([
            today,
            job.get("title"),
            job.get("company_name"),
            job.get("location"),
            job.get("via"), # Source job board (e.g., "via Indeed", "via Workopolis")
            job.get("detected_extensions", {}).get("posted_at")
        ])
