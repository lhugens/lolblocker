#import smtplib
#
#smtpserver = smtplib.SMTP("smtp.gmail.com", 587)
#smtpserver.ehlo()
#smtpserver.starttls()
#smtpserver.ehlo()
#smtpserver.login(email_user, email_pass)

import imaplib, email, email.header, datetime

mail = imaplib.IMAP4_SSL('imap.gmail.com', 993)
mail.login(email_user, email_pass)
mail.select('Inbox')

type, data = mail.search(None, 'ALL')
mail_ids = data[0]
id_list = mail_ids.split()

for num in data[0].split():
    print('---------------------------------')
    rv, data = mail.fetch(num, '(RFC822)')
    msg = email.message_from_bytes(data[0][1])
    hdr = email.header.make_header(email.header.decode_header(msg['Subject']))
    subject = str(hdr)
    print('Message %s: %s' % (num, subject))
    print('Raw Date:', msg['Date'])
    # Now convert to local date-time
    date_tuple = email.utils.parsedate_tz(msg['Date'])
    if date_tuple:
        local_date = datetime.datetime.fromtimestamp(
            email.utils.mktime_tz(date_tuple))
        print ("Local Date:", \
            local_date.strftime("%a, %d %b %Y %H:%M:%S"))

#for num in data[0].split():
#    print('---------------------------------')
#    rv, data = mail.fetch(num, '(RFC822)')
#    if rv != 'OK':
#        print("ERROR getting message", num)
#    
#    msg = email.message_from_bytes(data[0][1])
#    hdr = email.header.make_header(email.header.decode_header(msg['Subject']))
#    subject = str(hdr)
#    print('Message %s: %s' % (num, subject))
#    print('Raw Date:', msg['Date'])
#    # Now convert to local date-time
#    date_tuple = email.utils.parsedate_tz(msg['Date'])
#    if date_tuple:
#        local_date = datetime.datetime.fromtimestamp(
#            email.utils.mktime_tz(date_tuple))
#        print ("Local Date:", \
#            local_date.strftime("%a, %d %b %Y %H:%M:%S"))

