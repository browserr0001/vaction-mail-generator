import smtplib
import random
import time
import imaplib
import email
import traceback

GMAIL_USERNAME = "your_mail_id"
GMAIL_PASSWORD = "kwvorykgwhylcmqe"
IMAP_HOST = "imap.gmail.com"
IMAP_PORT = 993
MIN_INTERVAL = 45
MAX_INTERVAL = 120

replied_emails = set()  # Set to store replied email IDs

def check_new_emails():
    try:
        # Connect to the IMAP server
        imap_server = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT)
        imap_server.login(GMAIL_USERNAME, GMAIL_PASSWORD)
        imap_server.select("INBOX")

        # Search for unread emails
        _, data = imap_server.search(None, "UNSEEN")
        email_ids = data[0].split()

        if len(email_ids) == 0:
            print("No new mails")
            return

        # Loop through the email IDs
        for email_id in email_ids:
            if email_id not in replied_emails:
                # Fetch the email
                _, data = imap_server.fetch(email_id, "(RFC822)")
                _, message_data = data[0]
                message = email.message_from_bytes(message_data)

                # Check if the email has no prior replies
                if not has_prior_replies(imap_server, message):
                    # Reply to the email
                    reply_message = create_reply_message(message)
                    send_reply(reply_message)

                    # Add label and move the email to the labeled folder
                    add_label_and_move_email(imap_server, email_id)

                    # Mark the email as replied
                    replied_emails.add(email_id)
            else:
                    print("Already replied to"+str(email_id.decode()))

        # Close the IMAP connection
        imap_server.close()
        imap_server.logout()

    except imaplib.IMAP4.error as e:
        # Handle the IMAP error
        print("IMAP error occurred:", e)
        traceback.print_exc()

    except Exception as e:
        # Handle any other exception
        print("An error occurred:", e)
        traceback.print_exc()


def has_prior_replies(imap_server, message):
    if not label_exists(imap_server, "Replied"):
        return False

    _, data = imap_server.search(None, 'X-GM-LABELS "Replied"')
    email_ids = data[0].split()
    current_email_id = message["Message-ID"]

    if current_email_id in email_ids:
        return True
    else:
        return False


def label_exists(imap_server, label):
    try:
        _, data = imap_server.list()
        if data is None:
            return False
        for line in data:
            if label.encode("utf-8") in line:
                return True
        print()
    except Exception as e:
        print("An error occurred while checking labels:", e)
    return False


def create_reply_message(message):
    reply_message = email.message.EmailMessage()
    reply_message["Subject"] = "Re: " + message["Subject"]
    reply_message["From"] = GMAIL_USERNAME
    reply_message["To"] = message["From"]
    reply_message.set_content("I am currently out of the office and will be back on [date]. I will get back to you as soon as possible.")
    return reply_message


def send_reply(reply_message):
    # Send the reply message using SMTP
    smtp_server = smtplib.SMTP("smtp.gmail.com", 587)
    smtp_server.starttls()
    smtp_server.login(GMAIL_USERNAME, GMAIL_PASSWORD)
    smtp_server.send_message(reply_message)
    smtp_server.quit()


def add_label_and_move_email(imap_server, email_id):
    # Add a label to the email
    imap_server.store(email_id, "+X-GM-LABELS", "Replied")
    print("Label added")
    # Move the email to the labeled folder
    imap_server.copy(email_id, "Replied")
    print("Message moved")
    imap_server.store(email_id, "+FLAGS", "\\Deleted")
    imap_server.expunge()


if __name__ == "__main__":
    while True:
        # Check for new emails
        check_new_emails()
        print("---One cycle completed---")
        # Generate a random interval for the next check
        interval = 20
        print("----Sleeping-----")
        # Wait for the next check
        time.sleep(interval)
        print("Next cycle")
