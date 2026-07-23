import csv
from datetime import date
import os
from serpapi import GoogleSearch

api_key = os.environ.get('SERPAPI_KEY')

params = {
    'engine': 'google_jobs',
    'q': 'junior accountant OR junior bookkeeper',
    'location': 'Ottawa, Ontario, Canada',
    'hl': 'en',
    'api_key': api_key,
}

search = GoogleSearch(params)
results = search.get_dict()
jobs = results.get('jobs_results', [])

today = date.today().isoformat()
print(f'[{today}] Total entry-level postings found: {len(jobs)}')

# Versioned filename
raw_filename = f'data/raw_ottawa_jobs_{today}.csv'

# Check if file already exists before opening it
file_exists = os.path.exists(raw_filename)

# Open the file and keep all writing operations indented INSIDE this block
with open(raw_filename, 'a', newline='', encoding='utf-8') as file:
  writer = csv.writer(file)

  # Write header only if the file is brand new
  if not file_exists:
    writer.writerow([
        'date_posted',
        'job_title',
        'company',
        'location',
        'source',
        'posted_at_text',
        'description',
    ])

  # Write all job rows inside the 'with' block
  for job in jobs:
    writer.writerow([
        today,
        job.get('title'),
        job.get('company_name'),
        job.get('location'),
        job.get('via'),
        job.get('detected_extensions', {}).get('posted_at'),
        job.get('description'),
    ])

print(f'Raw data successfully saved to {raw_filename}')
