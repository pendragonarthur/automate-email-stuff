import os
import re
import smtplib
import imaplib
import email
from email.header import decode_header
from dotenv import load_dotenv

load_dotenv()

email_account = os.getenv('EMAIL_ACCOUNT')
auth_password = os.getenv('AUTH_PASSWORD')
imap_server = os.getenv('IMAP_SERVER')
smtp_server = os.getenv('SMTP_SERVER')

# Lista de emails que devem ser automaticamente ignorados por qualquer motivo
trashcan_mails = os.getenv('TRASHCAN_EMAILS')
trashmails_list = trashcan_mails.split(',') 

def regulate_email(text):
    match = re.search(r'<(.+?)>', text)
    if match:
        return match.group(1)
    return None


def find_useless_emails():
    # Email connection
    mail = imaplib.IMAP4_SSL(imap_server)
    mail.login(email_account, auth_password)
    print(f'Login successfull! Current account: {email_account}')
    mail.select('inbox')

    # Variables
    senders_list = []

    status, messages = mail.search(None, 'ALL')

    if status != 'OK':
        print('Failed to access inbox.')
        return
    
    email_ids = messages[0].decode().split()

    for email_id in email_ids:

        status, data = mail.fetch(email_id, '(RFC822)')

        if status != 'OK':
            print(f'Failed fetching email data. Email ID: {email_id}')

        raw_data = data[0][1]
        filtered_data = email.message_from_bytes(raw_data)
        sender = decode_header(filtered_data.get("From"))[0][0]
        decoded_sender = regulate_email(sender)
        print(decoded_sender)

        if sender in trashmails_list:
            senders_list.append(sender) 
            mail.store(email_id, '+FLAGS', '\\Deleted')

            print(f'Deleting emails from: {senders_list}')
                
            option = input(f'Are you sure you want to procede? (Y/N)').lower()
                
            if option != 'y':
                print('Canceling deletion.')

    print("No trashcan emails found. Good!")

           
find_useless_emails()