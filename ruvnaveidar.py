#!/usr/bin/env python

import argparse
import json
from ruvnaveidar_utils import *
import os

if __name__ == '__main__':
  parser = argparse.ArgumentParser()

  parser.add_argument('-o', '--output', help = 'Output directory for downloads.', default = 'out')
  parser.add_argument('-l', '--filelist', help = 'Only list all RÚV programs and write to file.', default = '')
  parser.add_argument('-v', '--verbose', action = 'store_true')

  args = parser.parse_args()

  api_data = fetch_programs()
  whitelist = list(read_file_list('whitelist.txt'))
  blacklist = read_file_list('blacklist.txt')
  seen_pids = set() # Note which programs have been checked

  if not os.path.exists(args.output):
    os.makedirs(args.output)

  for panel in api_data:
    # panel["format"] is either "tv" or "radio". All radio streams are ignored
    if panel['format'] != 'tv':
      continue

    pid = panel['id']

    if pid in seen_pids:
      continue

    seen_pids.add(pid)

    if len(args.filelist) > 0:
      with open(args.filelist, 'r', encoding='utf-8') as f:
        print(panel['id'], panel['title'])
      continue

    p_title = trim_season_number_suffix(panel['title'])

    if not is_title_in_list(whitelist, p_title):
      continue

    if args.verbose:
      print('#Matched "{}"'.format(p_title))
    ruv_api_program = 'https://api.ruv.is/api/programs/program/{}/all'.format(pid)
    p_r = get_url(ruv_api_program)

    if str(p_r) == '<Response [404]>':
      ruv_api_program2 = 'https://api.ruv.is/api/programs/get_ids/{}'.format(pid)
      p_r = get_url(ruv_api_program2)
      if str(p_r) == '<Response [404]>':
        continue

    try:
      p_data = p_r.json()
    except:
      print('ERROR: Failed reading JSON data from RÚV for pid={}'.format(pid))
      raise

    p_data = p_data['programs'] if 'programs' in p_data else p_data
    p_data = p_data if isinstance(p_data, list) else [p_data]

    for program in p_data:
      season_num = get_season_number_suffix(panel['title'])

      if "foreign_title" in program and len(program['foreign_title']) > 0:
        title = trim_season_number_suffix(program['foreign_title'])
      else:
        title = p_title

      for episode in program['episodes']:
        eid = episode['id']
        full_id = '{}|{}'.format(pid, eid)

        if full_id in blacklist:
          continue

        ep_num = str(episode['number']).zfill(2)
        out_fn = args.output + '/' + title
        out_fn += ' - S{}E{} - {}.ts'.format(season_num, ep_num, episode['title'])
        cmd = 'streamlink --output "{}" {} best'.format(out_fn, episode['file'])
        cmd +=  ' && echo "{}|{}" >> blacklist.txt'.format(pid, eid)
        print(cmd)
