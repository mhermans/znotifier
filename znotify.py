#!/usr/bin/env python
# coding: utf-8

from pyzotero import zotero
from datetime import datetime
from lxml import etree, html

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# SET GLOBAL VARIABLES
# ====================

SMTP_HOST = 'smtp.webfaction.com'
SMTP_LOGIN = ""
SMTP_PWD = ""

# WIN library
#library_id = '297624'
#library_type = 'group'
#api_key = 'Gl1kS04LvCAQ4fCcDHWGxKDh'

LIBRARY_ID = '313564'
LIBRARY_TYPE = 'group'
API_KEY = 'p3dRgO8Pe85xdFRHWfhNvfrw'

EMAIL_FROM = "maarten@mhermans.net"
#EMAIL_TO = "Laurianne.Terlinden@kuleuven.be"
EMAIL_TO = "maarten.hermans@kuleuven.be"


# FETCH ALL ZOTERO TOP ITEMS
# ==========================

# since looks at modification, not addition
#items = zot.top(sort='dateModified', direction='desc', since=60)
zot = zotero.Zotero(library_id, library_type, api_key)
items = zot.top(sort='dateModified', direction='desc')
citations = zot.top(sort='dateModified', direction='desc', content='citation')


# read/get previous generation time
prev_datetime = datetime.strptime(u'2014-12-11T11:11:33Z', "%Y-%m-%dT%H:%M:%SZ")

# select added since from previous data
filtered_items = [item for item in items if 
                  datetime.strptime(item['data']['dateAdded'], "%Y-%m-%dT%H:%M:%SZ") > prev_datetime ]
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
html_str = """<html>
                <head>
                    <meta http-equiv="Content-Type" content="text/html; charset=utf-8"> 
                <head>
                <body> 
                    <p>Documents added to the SESAME group library since %s:</p>
                    <ul>%s</ul>
		    <p>This email was generated automatically. Please send comments to <a href="mailto:laurianne.terlinden@kuleuven.be">Laurianne.Terlinden@kuleuven.be</a>.</p>
                </body>
            </html>""" % (prev_datetime, filtered_citations)


document_root = html.fromstring(html_str)
with open('out.html', 'w') as f:
    f.write(etree.tostring(document_root, encoding='utf-8', pretty_print=True))



# CREATE AND SEND HTML MESSAGE
# ============================

# Create message container - the correct MIME type is multipart/alternative.
msg = MIMEMultipart('alternative')
msg['Subject'] = "Recent additions to the SESAME group library"
msg['From'] = EMAIL_FROM
msg['To'] = EMAIL_TO 

# Record the MIME types of both parts - text/plain and text/html.
part = MIMEText(html_str.encode('utf-8'), 'html')
msg.attach(part)


# Send the message via local SMTP server.
s = smtplib.SMTP(SMTP_HOST)
s.login(SMTP_LOGIN, SMTP_PWD)
# sendmail function takes 3 arguments: sender's address, recipient's address
# and message to send - here it is sent as one string.
s.sendmail(me, you, msg.as_string())
s.quit()
