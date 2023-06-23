import smtplib
import random
import time
import imaplib
import email
import traceback

username = "your_mail"
password = "google_app_key"
IMAP_HOST = "imap.gmail.com"
IMAP_PORT = 993
min = 45
min = 120

replied_emails = set() 

def check_new_emails():
    try:
        # Connect to the IMAP server
        imap_serv = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT)
        imap_serv.login(username, password)
        imap_serv.select("INBOX")

        #unread emails
        _, data = imap_serv.search(None, "UNSEEN")
        email_ids = data[0].split()

        if len(email_ids) == 0:
            print("No new mails")
            return

        #email IDs
        for email_id in email_ids:
            if email_id not in replied_emails:
                _, data = imap_serv.fetch(email_id, "(RFC822)")
                _, mssg_data = data[0]
                mssg = email.message_from_bytes(mssg_data)
                # not to repeat replies
                if not has_prior_replies(imap_serv, mssg):
                    reply_mssg = create_reply_message(mssg)
                    send_reply(reply_mssg)

                    # label addition
                    add_label_and_move_email(imap_serv, email_id)

                    replied_emails.add(email_id)
            else:
                    print("Already replied to"+str(email_id.decode()))

        imap_serv.close()
        imap_serv.logout()
    #error handling
    except imaplib.IMAP4.error as e:
        print("IMAP error occurred:", e)
        traceback.print_exc()

    except Exception as e:
        print("An error occurred:", e)
        traceback.print_exc()


def has_prior_replies(imap_serv, mssg):
    if not label_exists(imap_serv, "Replied"):
        return False

    _, data = imap_serv.search(None, 'X-GM-LABELS "Replied"')
    email_ids = data[0].split()
    current_email_id = mssg["Message-ID"]

    if current_email_id in email_ids:
        return True
    else:
        return False


def label_exists(imap_serv, label):
    #checking the label
    try:
        _, data = imap_serv.list()
        if data is None:
            return False
        for line in data:
            if label.encode("utf-8") in line:
                return True
        print()
    except Exception as e:
        print("An error occurred while checking labels:", e)
    return False


def create_reply_message(mssg):
    reply_mssg = email.mssg.EmailMessage()
    reply_mssg["Subject"] = "Re: " + mssg["Subject"]
    reply_mssg["From"] = username
    reply_mssg["To"] = mssg["From"]
    reply_mssg.set_content("I am currently out of the office and will be back on [date]. I will get back to you as soon as possible.")
    return reply_mssg


def send_reply(reply_mssg):
    # SMTP
    smtp_server = smtplib.SMTP("smtp.gmail.com", 587)
    smtp_server.starttls()
    smtp_server.login(username, password)
    smtp_server.send_message(reply_mssg)
    smtp_server.quit()


def add_label_and_move_email(imap_serv, email_id):
    #additing label
    imap_serv.store(email_id, "+X-GM-LABELS", "Replied")
    print("Label added")
    # Move the email
    imap_serv.copy(email_id, "Replied")
    print("Message moved")
    imap_serv.store(email_id, "+FLAGS", "\\Deleted")
    imap_serv.expunge()


if __name__ == "__main__":
    while True:
        # Check for new emails
        check_new_emails()
        print("---One cycle completed---")
        interval = random.randint(min, min)
        print("----Sleeping-----")
        # Sleep for a while
        time.sleep(interval)
        print("Next cycle")
