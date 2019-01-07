#!/usr/bin/env python3
import string
import random
import configparser
from os.path import expanduser, join
import sys

import requests
from icalendar.cal import Calendar


CALDAVURL = '%sremote.php/dav/calendars/%s/%s'

def do_import(username, password, calendar, server, ics_url):
  base_url = CALDAVURL % (server, username, calendar)

  # fetch events from target cal
  target_fetch_url = '%s?export' % base_url
  r = requests.get(target_fetch_url, auth=(username, password))
  r.raise_for_status()
  try:
    target_cal = Calendar.from_ical(r.text)
  except ValueError as e:
    print('Warning: Could not parse iCal (%s)' % target_fetch_url,
          file=sys.stderr)
    print(e, file=sys.stderr)
    return

  existing_uids = []
  for e in target_cal.walk('VEVENT'):
    uid = bytes.decode(e['UID'].to_ical()).replace('\'', '').replace('/', 'slash')
    existing_uids.append(uid)

  # fetch webcal
  sourceRequest = requests.get(ics_url)
  sourceRequest.encoding = 'utf-8'
  sourceContent = sourceRequest.text
  c = Calendar.from_ical(sourceContent)

  # import webcal
  imported_uids = []
  for e in c.walk('VEVENT'):
    uid = bytes.decode(e['UID'].to_ical())
    uid.replace('\'','')
    uid.replace('/','slash')
    cal = Calendar()
    cal.add_component(e)
    r = requests.put('%s/%s.ics' % (base_url, uid),
                     data=cal.to_ical(),
                     auth=(username, password),
                     headers={'content-type':'text/calendar; charset=UTF-8'}
                     )
    if r.status_code == 500 and r'Sabre\VObject\Recur\NoInstancesException' in r.text:
      # ignore the NoInstancesException
      print('Warning: No valid instances: %s' % uid, file=sys.stdout)
    elif r.status_code == 201 or r.status_code == 204:
      print('Imported: %s (%d)' % (uid, r.status_code), file=sys.stdout)
      imported_uids.append(uid)
    else:
      r.raise_for_status()

  # remove events not in webcal
  for uid in existing_uids:
    if not uid in imported_uids:
      r = requests.delete('%s/%s.ics' % (base_url, uid),
                          auth=(username, password))
      if r.status_code == 204:
        print('Deleted %s' % uid, file=sys.stdout)
        # ignore 404 - not found (seems to be a manually created event)
      elif r.status_code == 404:
        pass
      else:
        r.raise_for_status()

if __name__ == '__main__':
  Config = configparser.RawConfigParser()
  Config.read(join(expanduser('~'), '.ics2owncloud.ini'))
  for key in Config.sections():
    try:
      do_import(Config.get(key, 'username'),
                Config.get(key, 'password'),
                Config.get(key, 'calendar'),
                Config.get(key, 'server'),
                Config.get(key, 'ics_url'),
                )
    except Exception as e:
      import traceback
      traceback.print_exc(file=sys.stderr)
