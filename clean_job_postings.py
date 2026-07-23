import re
import pandas as pd


def clean_job_postings(input_filepath: str, output_filepath: str) -> pd.DataFrame:
  """Cleans job posting data, removes cross-board duplicates, and categorizes by province."""
  # 1. Load Dataset
  try:
    df = pd.read_csv(input_filepath)
  except FileNotFoundError:
    print(f'Error: The file {input_filepath} was not found.')
    return pd.DataFrame()

  print(f'Initial record count: {len(df):,}')

  # 2. Standardize Text Columns
  text_columns = ['job_title', 'company', 'location', 'description', 'source']
  for col in text_columns:
    if col in df.columns:
      df[col] = df[col].astype(str).str.strip().str.lower()
      # Normalize internal whitespace
      df[col] = df[col].apply(lambda x: re.sub(r'\s+', ' ', x))

  # 3. Handle Missing Values
  # Essential fields required for a valid listing
  df.dropna(subset=['job_title', 'company'], inplace=True)

  # 4. Remove Cross-Board Duplicates
  # If an external tracking ID exists, use it to eliminate exact platform mirrors
  if 'external_id' in df.columns:
    df.drop_duplicates(subset=['external_id'], keep='first', inplace=True)

  # Fallback composite key deduplication (handles same job posted on LinkedIn, Indeed, etc.)
  df.drop_duplicates(
      subset=['job_title', 'company', 'location'], keep='first', inplace=True
  )
  print(f'Record count after deduplication: {len(df):,}')

  # 5. Categorize Roles by Province
  province_mapping = {
      'Ontario': [
          'ontario',
          'toronto',
          'ottawa',
          'mississauga',
          'hamilton',
          'waterloo',
          'london',
      ],
      'British Columbia': ['bc', 'british columbia', 'vancouver', 'victoria'],
      'Quebec': ['quebec', 'qc', 'montreal', 'quebec city'],
      'Alberta': ['alberta', 'ab', 'calgary', 'edmonton'],
      'Nova Scotia': ['nova scotia', 'ns', 'halifax'],
      'Manitoba': ['manitoba', 'mb', 'winnipeg'],
      'Saskatchewan': ['saskatchewan', 'sk', 'regina', 'saskatoon'],
  }

  def map_location_to_province(location_str: str) -> str:
    for province, keywords in province_mapping.items():
      for kw in keywords:
        if re.search(r'\b' + re.escape(kw) + r'\b', location_str):
          return province
    return 'Other / Remote'

  df['province'] = df['location'].apply(map_location_to_province)

  # 6. Parse Dates
  if 'date_posted' in df.columns:
    df['date_posted'] = pd.to_datetime(df['date_posted'], errors='coerce')

  # 7. Export Cleaned Data
  df.to_csv(output_filepath, index=False)
  print(f'Cleaned data successfully saved to {output_filepath}')

  return df


if __name__ == '__main__':
  # Configuration variables
  INPUT_FILE = 'raw_job_postings.csv'
  OUTPUT_FILE = 'cleaned_job_postings.csv'

  cleaned_df = clean_job_postings(INPUT_FILE, OUTPUT_FILE)

  if not cleaned_df.empty:
    print('\nBreakdown of postings by province:')
    print(cleaned_df['province'].value_counts())
