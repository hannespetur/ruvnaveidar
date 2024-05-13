import json
import os
import roman
from requests.adapters import HTTPAdapter # For Retrying
from requests.packages.urllib3.util.retry import Retry # For Retrying
import requests

##
# checks if string is a roman numeral
def is_roman_numeral(check):
  try:
    roman.fromRoman(check)
    return True
  except roman.InvalidRomanNumeralError:
    return False
  except:
    raise

# Creates a new retry session for the HTTP protocol
# See: https://www.peterbe.com/plog/best-practice-with-retries-with-requests
def get_url(url, retries=5):
  session = requests.Session()

  retry = Retry(
    total=retries,
    read=retries,
    connect=retries,
    backoff_factor=0.3,
    status_forcelist=(500, 502, 504))

  adapter = HTTPAdapter(max_retries=retry)
  session.mount('http://', adapter)
  session.mount('https://', adapter)
  return session.get(url)


assert(is_roman_numeral('Blæja') == False)
assert(is_roman_numeral('XI') == True)
assert(is_roman_numeral('I') == True)
assert(is_roman_numeral('1') == False)


# Removes any season number related suffixes for a given series title
# Ex. Monsurnar 1 => Monsurnar
#     Hvolpasveitin IV => Hvolpasveitin
def trim_season_number_suffix(title):
  title_words = title.split(' ')
  if len(title_words) >= 2 and (title_words[-1].isdigit() or is_roman_numeral(title_words[-1])):
    return ' '.join(title_words[0:-1])
  else:
    return title

def get_season_number_suffix(title):
  title_words = title.split(' ')

  if len(title_words) >= 2:
    if title_words[-1].isdigit():
      return title_words[-1].zfill(2)

    try:
      num = roman.fromRoman(title_words[-1])
      return str(num).zfill(2)
    except:
      pass

  return '99'


##
def is_title_in_list(whitelist, title):
  title = title.lower()
  for show in whitelist:
    if title.startswith(show):
      return True

  return False


## stores each line of a file in a set
def read_file_list(fn):
  s = set()

  if os.path.exists(fn):
    with open(fn, 'r', encoding='utf-8') as f:
      for line in f:
        if not line.startswith('#'):
          s.add(line.lower().rstrip())

  return s

## Fetch all RÚV programs
def fetch_programs():
  ruv_api_url_all = 'https://api.ruv.is/api/programs/all'
  ruv_api_url_featured = 'https://api.ruv.is/api/programs/featured/tv'
  api_data = None

  r = get_url(ruv_api_url_all)

  try:
    api_data = r.json()
  except:
    print('ERROR: Failed reading JSON data from RÚV for all programs (old API)')
    raise

  r = get_url(ruv_api_url_featured)

  try:
    api_data2 = r.json()['panels']
  except:
    print('ERROR: Failed reading JSON data from RÚV for all programs (new API)')
    raise

  for panel_data in api_data2:
    if 'programs' in panel_data:
      api_data.extend(panel_data['programs'])

  return api_data
