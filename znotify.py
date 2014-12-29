#!/usr/bin/env python
# coding: utf-8

from pyzotero import zotero
from datetime import datetime, timedelta
from lxml import etree, html

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from ConfigParser import SafeConfigParser

SETTINGSFILE = '/home/mhermans/znotifier/settings.ini'

# SET GLOBAL VARIABLES
# ====================

parser = SafeConfigParser()
parser.read(SETTINGSFILE)


# FETCH ALL ZOTERO TOP ITEMS
# ==========================

zot = zotero.Zotero(parser.get('zotero', 'LIBRARY_ID'),
                    'group', parser.get('zotero', 'API_KEY'))

# fetch twice, raw data and formatted HTML-citations
items = zot.top(sort='dateModified', direction='desc')
citations = zot.top(sort='dateModified', direction='desc', content='citation')


# SELECT ONLY FOR THE LAST X DAYS
# ===============================

prev_datetime = datetime.today() - timedelta(
    days=parser.get('zotero', 'DAYS_DELTA'))

# filter items added during interval
filtered_items = [item for item in items if
                  datetime.strptime(
                      item['data']['dateAdded'], "%Y-%m-%dT%H:%M:%SZ") >
                  prev_datetime]

filtered_citations = citations[0:len(filtered_items)]


# create html list items with link & creator
for i, filtered_citation in enumerate(filtered_citations):
    user = filtered_items[i]['meta']['createdByUser']['username']
    link = filtered_items[i]['links']['alternate']['href']
    row = """<li>%s <span>(<a href="%s"><strong>link</strong></a>,
                added by <em>%s</em>)</span></li>""" % (filtered_citation, link, user)
    filtered_citations[i] = ''.join(row)

filtered_citations = ' '.join(filtered_citations)


# fill in html template and write out to be sure
html_str = """
<html>
    <head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <head>
    <body>
        <p>Dear members</p>
        <p>The following documents were added to the Zotero
            group library since %s (the past week):</p>
        <ul>%s</ul>
        <p><em>This email was generated automatically.
            Please send comments to <a href="mailto:%s">%s</a>.</em></p>
    </body>
</html>""" % (prev_datetime.date(), filtered_citations,
              parser.get('email', 'EMAIL_FROM'),
              parser.get('email', 'EMAIL_FROM'))

# write out html message
document_root = html.fromstring(html_str)
with open('out.html', 'w') as f:
    f.write(etree.tostring(document_root, encoding='utf-8', pretty_print=True))


# CREATE AND SEND HTML MESSAGE
# ============================

# Create message container - the correct MIME type is multipart/alternative.
msg = MIMEMultipart('alternative')
msg['Subject'] = "Recent additions to the Zotero group library"
msg['From'] = parser.get('email', 'EMAIL_FROM')
msg['To'] = parser.get('email', 'EMAIL_TO')
# msg['Cc'] = parser.get('email', 'EMAIL_CC')

# Record the MIME type as text/html.
part = MIMEText(html_str.encode('utf-8'), 'html')
msg.attach(part)

# Send the message via (local) SMTP server.
s = smtplib.SMTP(parser.get('smtp', 'SMTP_HOST'))
s.login(parser.get('smtp', 'SMTP_LOGIN'), parser.get('smtp', 'SMTP_PWD'))

# sendmail function takes 3 arguments: sender's address, recipient's address
s.sendmail(
    parser.get('email', 'EMAIL_FROM'),
    parser.get('email', 'EMAIL_TO'),
    msg.as_string())
s.quit()
