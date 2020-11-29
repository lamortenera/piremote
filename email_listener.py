from imapclient import IMAPClient

import email
import logging
import smtplib

#import logging; logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s', level=logging.DEBUG)


EMAIL = "ale.fener@gmail.com"
PASSWORD = "niazyrsczqwvxsyi"
SERVER = "imap.gmail.com"
SERVER2 = "smtp.gmail.com"

email_template = "From: {}\nTo: {}\nSubject: {}\n"
if True:
    msg = "Ciao, questa e' una prova"
    server = smtplib.SMTP_SSL(SERVER2, 465)
    server.ehlo()
    server.login(EMAIL, PASSWORD)
    server.sendmail(EMAIL, EMAIL, email_template.format(EMAIL, EMAIL, msg))
    server.close()
    print("Email sent!!")

if False:
    mail = IMAPClient(SERVER, use_uid=False)
    mail.login(EMAIL, PASSWORD)
    mail.select_folder('INBOX')
    # Start IDLE mode
    mail.idle()
    print("idling")
    print("Connection is now in IDLE mode, send yourself an email or quit with ^c")

    while True:
        try:
            # Wait for up to 30 seconds for an IDLE response
            responses = mail.idle_check(timeout=30)
            mail.idle_done()
            #print("Server sent:", responses if responses else "nothing")
            for r in responses:
                #print(f"processing response {r}")
                if len(r) < 2:
                    #print("invalid length")
                    continue
                if r[1] != b'EXISTS':
                    #print(f"{r[1]} != b'EXISTS'")
                    continue
                num = r[0]
                #print(f"Fetching {num}")
                data = mail.fetch([num], 'RFC822')
                #print("fetch complete with keys: {}".format(data.keys()))
                if not num in data.keys():
                    #print("Message can't be fetched")
                    continue
                msg = email.message_from_bytes(data[num][b'RFC822'])
                print(f"got:{msg.get('Subject')}")
            mail.idle()
        except KeyboardInterrupt:
            break

    mail.idle_done()
    print("\nIDLE mode done")
    mail.logout()
