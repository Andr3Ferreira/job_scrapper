from serpapi import GoogleSearch
import json
import csv
import os
from datetime import date

# Get API key securely from GitHub environment variables
api_key = os.environ.get('SERPAPI_KEY')

# Define your target search parameters
params = {
    "engine": "google_jobs",
    "q": "junior accountant OR junior bookkeeper OR accountanting assistant OR accountant assistant OR accounting clerk",
    "location": "Ottawa, Ontario, Canada",
    "hl": "en",
    "api_key": api_key # Free tier offers 100 searches/month
}

search = GoogleSearch(params)
results = search.get_dict()
jobs = results.get("jobs_results", [])

# Append summary counts & job details to a daily dataset
today = date.today().isoformat()
print(f"[{today}] Total entry-level postings found: {len(jobs)}")

raw_filename = f'data/raw_ottawa_jobs_{today}.csv'

with open(raw_filename, 'w', newline='', encoding='utf-8') as file:
  writer = csv.writer(file)

if not file_exists:
  writer.writerow([
      'date_posted',
      'job_title',
      'company',
      'location',
      'source',
      'posted_at_text',
      'description',  # Added column
  ])

# 2. Update the row data being written
for job in jobs:
  writer.writerow([
      today,
      job.get('title'),
      job.get('company_name'),
      job.get('location'),
      job.get('via'),
      job.get('detected_extensions', {}).get('posted_at'),
      job.get('description'),  # Captures the full job description text
  ])
