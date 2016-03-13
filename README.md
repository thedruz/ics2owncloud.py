# ics2owncloud.py

After [this solution](http://zeit-zu-handeln.net/2014/02/allgemein/owncloud-6-kalender-ical-feeds-importierenexportieren/)
stopped working in ownCloud 9 I had to come up with something else to make periodical iCal imports work.

This script downloads iCal files and imports them into ownCloud using CalDAV.

## Requirements

* Virtualenv

## Installation

    $ git clone https://github.com/buzz/ics2owncloud.py.git

## Configuration

### Configuration file

Create and edit config file:

    cp ics2owncloud.ini.example ~/.ics2owncloud.ini

A config file with two entries looks like this:

    [DEFAULT]
    username: tom
    password: 123456
    server: https://cloud.example.com/

    [import_a]
    calendar: calendar_xy
    ics_url: https://USER1:XXX@cloud.owncloud.org/index.php/apps/calendar/export.php?calid=6

    [import_b]
    calendar: facebook
    ics_url: https://www.facebook.com/ical/u.php?uid=10000123456789&key=ABCDEFGHIJKL

* `username` - ownCloud user
* `password` - ownCloud password
* `server` - ownCloud server URI
* `calender` - ownCloud calendar name
* `ics_url` - URL to the ICS file to download (can have username:password format)

### Cron job

A cron job comes in handy to periodically import calendars:

    $ crontab -e

This runs the script every 30 minutes:

    */30 * * * * /PATH/TO/ics2owncloud.sh >/dev/null