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


def read_file_list(fn):
  """Stores each line of a file in a set"""
  s = set()

  if os.path.exists(fn):
    with open(fn, 'r', encoding='utf-8') as f:
      for line in f:
        if not line.startswith('#'):
          s.add(line.lower().rstrip())

  return s


def read_pid2fix(fn):
  """
  Reads a file containing a program ID (pid) and a fixed program name (title), including the season (S0X) and,
  makes a dict.

  The pid and title both strings and should be separated with a TAB ("\t"):

  Example:
  34298\tSmástund S02
  34233\tCurious George (2006) S04
  """
  d = dict()

  if os.path.exists(fn):
    with open(fn, 'r', encoding='utf-8') as f:
      for line in f:
        if line.startswith('#'):
          continue

        split_line = line.split('\t')

        if len(split_line) != 2:
          print("WARNING: Skipping a pid2fix line with {} fields".format(len(split_line)))
          continue

        d[split_line[0]] = split_line[1].rstrip()

  return d

def fetch_programs():
  """
  Fetches a list all RÚV programs.

  Fetched data is a program list where each program contains information about TV shows/movies available. It
  does not contain any information about which episodes are available, that data is requested later. Each
  program MAY have the following fields (needs to be checked):
   * id: Program ID (pid)
   * title: Title of the program
   * format: radio or tv
   * channel: i.e. RÚV, Rás 2
   * foreign_title
   * slug
   * image
   * portrait_image
   * description
   * short_description
   * categories
   * multiple_episodes
   * vod_available_episodes
   * web_available_episodes
   * podcast_available_episodes
   * web_latest_date
   * episodes
   * podcast
   * last_updated
   * panels
   * reverse_episode_order
  """
  ruv_api_url_featured = 'https://api.ruv.is/api/programs/featured/tv'
  api_data = None

  r = get_url(ruv_api_url_featured)

  try:
    api_data = r.json()
  except:
    print('ERROR: Failed reading JSON data from RÚV for all programs (new API)')
    raise

  all_panel_data = api_data['panels'] if 'panels' in api_data else None  
  data = []
  
  for panel_data in all_panel_data:
    if 'programs' in panel_data:
      data.extend(panel_data['programs'])
  
  data = list({item['id']:item for item in data}.values())
  
  return data
