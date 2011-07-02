#!/usr/bin/python

import re, mechanize, datetime, urllib, smtplib, string

# Parameters that need to be changed
user_name = ''
password = ''
report_days = 5
mail_server = 'localhost'
mail_to = ''
mail_from = ''
mail_subject = 'RR API Report'

# Parameters that shouldn't be touched
params = {'saved_search':'mapi_calls_made',
          'tqx':'reqId=1',
          'start':'',
          'end':'',
          'mapi':'',
          'spkey':''}
report_url = 'http://developer.rottentomatoes.com/reports/lookup?'
login_url = 'https://secure.mashery.com/login/developer.rottentomatoes.com/'
year = str(datetime.datetime.now().year)

# Create a ISO9601 date string. Taken from the mashery JS code.
def get_ISO9601_string(year, month, date):
    return str(year) + '-' + str(month) + '-' + str(date) + 'T0:0:0GMT'

# Extract the stats into an array of strings from the reports
# lookup response.
def extract_stats(response):
    # get all stats from the response
    statsMatch = re.findall(r'f:\'([\w\d ]+)\'', response, re.DOTALL)
    stats = []
    # format the stats with the date
    try:
        for i in xrange(0, len(statsMatch), 3):
            stats.append(statsMatch[i]+' - '+statsMatch[i+2])
    except IndexError:
        stats = []
        for i in xrange(0, len(statsMatch), 2):
            stats.append(statsMatch[i]+' - '+statsMatch[i+1])

    return stats

# Format the stats for the email
def format_stats(stats):
    return '\n'.join(stats);

# Send an email.
def send_mail(stats):
    body = string.join((
        'From: %s' % mail_from,
        'To: %s' % mail_to,
        'Subject: %s' % mail_subject,
        '',
        stats
    ), '\r\n')

    server = smtplib.SMTP(mail_server)
    server.sendmail(mail_from, [mail_to], body)
    server.quit()
         
def main():
    # load login url
    br = mechanize.Browser()
    br.open(login_url)
    # submit username and password
    br.select_form(nr=0)
    br['handle'] = user_name
    br['passwd'] = password
    br.submit()
    # get to the report page for the first registered api key
    response = br.follow_link(text_regex='My Account', nr=0)
    response = br.follow_link(text_regex='View Report', nr=0)
    # get the user key and api key
    url_split = br.geturl().split('/')
    params['spkey'] = url_split[5]
    params['mapi'] = url_split[6]
    # create and format the start and end dates for the report
    end = datetime.datetime.utcnow() + datetime.timedelta(days=1)
    start = end - datetime.timedelta(days=report_days)
    params['start'] = get_ISO9601_string(start.year, start.month, start.day)
    params['end'] = get_ISO9601_string(end.year, end.month, end.day)
    # load report data
    br.open(report_url + urllib.urlencode(params))
    # extract api stats from report data
    stats = extract_stats(br.response().read())
    # send email with stats
    send_mail(format_stats(stats))

main()    





