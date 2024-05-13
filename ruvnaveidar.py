#!/usr/bin/env python

import json
import requests
from requests.adapters import HTTPAdapter # For Retrying
from requests.packages.urllib3.util.retry import Retry # For Retrying
import roman
import sys
import os


# Creates a new retry session for the HTTP protocol
# See: https://www.peterbe.com/plog/best-practice-with-retries-with-requests
def __create_retry_session(retries=5):
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
  return session

def is_roman_numeral(check):
  try:
    roman.fromRoman(check)
    return True
  except:
    return False

assert(is_roman_numeral("Blæja") == False)
assert(is_roman_numeral("XI") == True)
assert(is_roman_numeral("I") == True)
assert(is_roman_numeral("1") == False)

# Removes any season number related suffixes for a given series title
# Ex. Monsurnar 1 => Monsurnar
#     Hvolpasveitin IV => Hvolpasveitin
def trim_season_number_suffix(title):
  title_words = title.split(" ")
  if len(title_words) >= 2 and (title_words[-1].isdigit() or is_roman_numeral(title_words[-1])):
    return " ".join(title_words[0:-1])
  else:
    return title

def get_season_number_suffix(title):
  title_words = title.split(" ")

  if len(title_words) >= 2:
    if title_words[-1].isdigit():
      return title_words[-1].zfill(2)

    try:
      num = roman.fromRoman(title_words[-1])
      return str(num).zfill(2)
    except:
      pass

  return "99"


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
    with open(fn, "r") as f:
      for line in f:
        if not line.startswith("#"):
          s.add(line.lower().rstrip())

  return s

## Fetch all RÚV programs
def fetch_programs(is_updated = True):
  ruv_api_url_all = 'https://api.ruv.is/api/programs/all'
  ruv_api_url_featured = 'https://api.ruv.is/api/programs/featured/tv'
  api_data = None

  if is_updated or not os.path.exists("data_list.json"):
    r = __create_retry_session().get(ruv_api_url_all)
    api_data = r.json()

    r = __create_retry_session().get(ruv_api_url_featured)
    api_data2 = r.json()["panels"]

    for panel_data in api_data2:
      if 'programs' in panel_data:
        api_data.extend(panel_data['programs'])

    with open("data.json", "w") as f:
      json.dump(api_data, f)
  else:
    f = open("data.json")
    api_data = json.load(f)

  return api_data

## Main
api_data = fetch_programs(is_updated=True)
whitelist = list(read_file_list("whitelist.txt"))
blacklist = read_file_list("blacklist.txt")
seen_pids = set()

for panel in api_data:
  if panel["format"] != "tv":
    continue

  p_title = trim_season_number_suffix(panel["title"])
  pid = panel["id"]

  if pid in seen_pids or not is_title_in_list(whitelist, p_title):
    continue

  seen_pids.add(pid)
  ruv_api_program = "https://api.ruv.is/api/programs/program/{}/all".format(pid)
  p_r = __create_retry_session().get(ruv_api_program)

  if str(p_r) == "<Response [404]>":
    ruv_api_program2 = "https://api.ruv.is/api/programs/get_ids/{}".format(pid)
    p_r = __create_retry_session().get(ruv_api_program2)
    if str(p_r) == "<Response [404]>":
      continue

  p_data = p_r.json()
  p_data = p_data["programs"] if "programs" in p_data else p_data
  p_data = p_data if isinstance(p_data, list) else [p_data]

  for program in p_data:
    season_num = get_season_number_suffix(panel["title"])

    if "foreign_title" in program and len(program["foreign_title"]) > 0:
      title = "{}".format(trim_season_number_suffix(program["foreign_title"]))
    else:
      title = p_title

    for episode in program["episodes"]:
      eid = episode["id"]
      full_id = "{}|{}".format(pid, eid)

      if full_id in blacklist:
        continue

      ep_num = str(episode["number"]).zfill(2)
      local_name = title + " - S{}E{} - {}.ts".format(season_num, ep_num, episode["title"])
      print('streamlink --output "{}" {} best && echo "{}|{}" >> blacklist.txt'.format(local_name, episode["file"], pid, eid))
