**znotifier** -  Python script to send automated emails with recent additions to a Zotero group library.

# Requirements

* [pyzotero](https://github.com/urschrei/pyzotero)
* API key with read-only access to the Zotero group library.
* `cron`

# Setup

* Install [pyzotero](https://github.com/urschrei/pyzotero): `pip install pyzotero`.
* Modify the path to `settings.ini` in `znotify.py` (use absolute paths when running cronjobs).
* Generate a API key for the Zotero group library through the Zotero.com web interface.
* Modify `settings.ini` itself: SMTP-settings, Zotero credentials, generation-interval in days (this needs to be the same interval as in the cronjob).
* Modify the `cronjob` example. Use absolute paths, and if you use `virtualenv`, remember to add the correct Python interpreter.
* Add the cronjob to `crontab` using `crontab cronjob`.

Change the basic HTML template in `znotify.py` to match your requirements.
