#!/usr/bin/env python
# coding: utf-8

from pyzotero import zotero
from datetime import datetime, timedelta
import smtplib
import sys
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from ConfigParser import SafeConfigParser

SETTINGSFILE = '/home/mhermans/znotifier/settings.ini'

# SET GLOBAL VARIABLES
# ====================

parser = SafeConfigParser()
parser.read(SETTINGSFILE)


# SETUP LOGGING
# =============

LOG_FILENAME = parser.get('base', 'LOG_FILENAME')
logging.basicConfig(
    filename=LOG_FILENAME,
    level=logging.DEBUG)

# FETCH ALL ZOTERO TOP ITEMS
# ==========================

zot = zotero.Zotero(
   parser.get('zotero', 'LIBRARY_ID'),
   'group',
    parser.get('zotero', 'API_KEY'))

# fetch twice, raw data and formatted HTML-citations
# limit is set to 150, raise if expected count in timespan is higher
data_items = zot.top(
    sort='dateModified',
    direction='desc',
    limit=150)

citation_items = zot.top(
    sort='dateModified',
    direction='desc',
    content='citation',
    limit=150)

if len(data_items) != len(citation_items):
    logging.error('Unequal lenghts for data and citation lists')
    raise ValueError('Unequal lengths for data and citation lists')

items = zip(data_items, citation_items)


# SELECT ONLY FOR THE LAST X DAYS
# ===============================

days_delta = int(parser.get('zotero', 'DAYS_DELTA'))
prev_datetime = datetime.today() - timedelta(days=days_delta)

# filter items added during interval
filtered_items = [item for item in items if
                  datetime.strptime(
                      item[0]['data']['dateAdded'], "%Y-%m-%dT%H:%M:%SZ") >
                  prev_datetime]
logging.info('Total number of filtered items: %s' % len(filtered_items))

# stop if no added citations in timespan
if len(filtered_items) == 0:
    logging.debug(
        'Zero items in span of %s day, stopping' % str(days_delta))
    sys.exit(0)

# create html list items with link & creator
citation_list = []
for data, citation in filtered_items:
    user = data['meta']['createdByUser']['username']
    link = data['links']['alternate']['href']
    row = """<li>%s <span>(<a href="%s"><strong>link</strong></a>,
                added by <em>%s</em>)</span></li>""" % (citation, link, user)
    citation_list.append(''.join(row))

citation_list = ' '.join(citation_list)

# fill in html template and write out to be sure
html_str = """
<html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <head>
    <body>
        <p>Dear members</p>
        <p>The following documents were added to the Zotero
            group library since %s:</p>
        <ul>%s</ul>
        <p><em>This email was generated automatically.
            Please send comments to <a href="mailto:%s">%s</a>.</em></p>
    </body>
</html>""" % (prev_datetime.date(), citation_list,
              parser.get('email', 'EMAIL_REPLY'),
              parser.get('email', 'EMAIL_REPLY'))

# optional: write out html message (local archive)
# required: pip install lxml
#
# from lxml import etree, html
# document_root = html.fromstring(html_str)
# with open('out.html', 'w') as f:
#    f.write(etree.tostring(document_root, encoding='utf-8', pretty_print=True))


# CREATE AND SEND HTML MESSAGE
# ============================

# Create message container - the correct MIME type is multipart/alternative.

recipients = [parser.get('email', 'EMAIL_TO'),
        parser.get('email', 'EMAIL_CC')]

logging.info('mailing to %s' % ', '.join(recipients))

msg = MIMEMultipart('alternative')
msg['Subject'] = "Recent additions to the Zotero group library"
msg['From'] = parser.get('email', 'EMAIL_FROM')
msg['To'] = ', '.join(recipients)
#msg['Cc'] = parser.get('email', 'EMAIL_CC')

# Record the MIME type as text/html.
part = MIMEText(html_str.encode('utf-8'), 'html')
msg.attach(part)

# Send the message via (local) SMTP server.
s = smtplib.SMTP(parser.get('smtp', 'SMTP_HOST'))
s.login(parser.get('smtp', 'SMTP_LOGIN'), parser.get('smtp', 'SMTP_PWD'))

# sendmail function takes 3 arguments: sender's address, recipient's address
# and message to send - here it is sent as one string.
s.sendmail(parser.get('email', 'EMAIL_FROM'), recipients, msg.as_string())
s.quit()
