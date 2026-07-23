import csv
from datetime import date
import json
import os
import re
from serpapi import GoogleSearch

api_key = os.environ.get('SERPAPI_KEY')

params = {
    'engine': 'google_jobs',
    'q': 'junior accountant OR junior bookkeeper OR accounting clerk OR accounts payable clerk OR accounts receivable clerk OR finance clerk OR bookkeeping assistant OR accounting assistant OR administrative bookkeeper OR junior accounting OR entry level accountant OR accountant assistant OR bookkeeper assistant',
    'location': 'Ottawa, Ontario, Canada',
    'hl': 'en',
    'api_key': api_key,
}

search = GoogleSearch(params)
results = search.get_dict()

# Check if SerpApi returned an account/quota error
if 'error' in results:
  print(f"[ERROR] SerpApi failure: {results['error']}")
  # Exit gracefully or raise a clear error message
  raise SystemExit(
      'Pipeline stopped: Your SerpApi account has run out of searches or the'
      ' API key is invalid.'
  )

jobs = results.get('jobs_results', [])

today = date.today().isoformat()
print(f'[{today}] Total entry-level postings found: {len(jobs)}')

output_dir = 'data'
raw_filename = os.path.join(output_dir, f'raw_ottawa_jobs_{today}.csv')
file_exists = os.path.exists(raw_filename)


# --- Extraction Functions ---
def extract_education(description: str) -> str:
  if not description:
    return 'Not Specified'
  desc_lower = description.lower()

  found_levels = []

  # Check for individual tiers
  has_designation = any(
      term in desc_lower
      for term in ['cpa', 'ca', 'cga', 'cma', 'master', 'mba']
  )
  has_bachelor = any(
      term in desc_lower
      for term in [
          'bachelor',
          'b.comm',
          'bba',
          'university degree',
          'undergraduate',
      ]
  )
  has_diploma = any(
      term in desc_lower
      for term in ['diploma', 'college certificate', 'accounting admin']
  )
  has_hs = 'high school' in desc_lower

  if has_designation:
    found_levels.append('Professional Designation / Master’s')
  if has_bachelor:
    found_levels.append("Bachelor's Degree")
  if has_diploma:
    found_levels.append('College Diploma')
  if has_hs:
    found_levels.append('High School')

  if not found_levels:
    return 'General / Unspecified'

  # If multiple tiers are found (e.g. "Bachelor's or College Diploma"), combine them
  if len(found_levels) > 1:
    return ' OR '.join(found_levels)

  return found_levels[0]


def extract_tech_skills(description: str) -> str:
  if not description:
    return json.dumps([])  # Store as a JSON-serialized list string for CSV safety

  desc_lower = description.lower()

  # Define common software, tools, and technical terms to look for
  skill_keywords = [
      'excel',
      'quickbooks',
      'sage',
      'xero',
      'erp',
      'sap',
      'sql',
      'vba',
      'power bi',
      'tableau',
      'gaap',
      'ifrs',
      'payroll',
      'tax',
      'bookkeeping',
      'python',
      'coda',
      'freshbooks',
  ]

  found_skills = [
      skill.upper() if len(skill) <= 4 else skill.capitalize()
      for skill in skill_keywords
      if re.search(r'\b' + re.escape(skill) + r'\b', desc_lower)
  ]

  # Return as a string representation of a list (Pandas can evaluate this back to a list easily)
  return json.dumps(list(set(found_skills)))

def extract_primary_link(job: dict) -> str:
  # SerpApi typically stores application links inside 'apply_options'
  apply_options = job.get('apply_options', [])
  if apply_options and isinstance(apply_options, list):
    # Return the first available application URL
    return apply_options[0].get('link', '')

  # Fallback if there's a direct share/job link property
  return job.get('share_link', '')


# --- Writing Data ---
with open(raw_filename, 'w', newline='', encoding='utf-8') as file:
  writer = csv.writer(file)

  # Updated header adding explicit columns
  writer.writerow([
      'date_posted',
      'job_title',
      'company',
      'location',
      'source',
      'posted_at_text',
      'education_requirement',
      'technical_skills',
      'description',
      'link',
  ])

  for job in jobs:
    desc = job.get('description', '')
    edu_req = extract_education(desc)
    tech_skills = extract_tech_skills(desc)
    job_link = extract_primary_link(job)  

    writer.writerow([
        today,
        job.get('title'),
        job.get('company_name'),
        job.get('location'),
        job.get('via'),
        job.get('detected_extensions', {}).get('posted_at'),
        edu_req,
        tech_skills,
        desc,
        job_link
    ])

print(f'Raw data successfully saved with extractions to {raw_filename}')

#----------- OLD VERSION -------------
# import csv
# from datetime import date
# import os
# from serpapi import GoogleSearch

# api_key = os.environ.get('SERPAPI_KEY')

# params = {
#     'engine': 'google_jobs',
#     'q': 'junior accountant OR junior bookkeeper',
#     'location': 'Ottawa, Ontario, Canada',
#     'hl': 'en',
#     'api_key': api_key,
# }

# search = GoogleSearch(params)
# results = search.get_dict()
# jobs = results.get('jobs_results', [])

# today = date.today().isoformat()
# print(f'[{today}] Total entry-level postings found: {len(jobs)}')

# # Versioned filename
# raw_filename = f'data/raw_ottawa_jobs_{today}.csv'

# # Check if file already exists before opening it
# file_exists = os.path.exists(raw_filename)

# # Open the file and keep all writing operations indented INSIDE this block
# with open(raw_filename, 'a', newline='', encoding='utf-8') as file:
#   writer = csv.writer(file)

#   # Write header only if the file is brand new
#   if not file_exists:
#     writer.writerow([
#         'date_posted',
#         'job_title',
#         'company',
#         'location',
#         'source',
#         'posted_at_text',
#         'description',
#     ])

#   # Write all job rows inside the 'with' block
#   for job in jobs:
#     writer.writerow([
#         today,
#         job.get('title'),
#         job.get('company_name'),
#         job.get('location'),
#         job.get('via'),
#         job.get('detected_extensions', {}).get('posted_at'),
#         job.get('description'),
#     ])

# print(f'Raw data successfully saved to {raw_filename}')
