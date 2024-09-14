import os
import smtplib
import imaplib
import email
from dotenv import load_dotenv

load_dotenv()

email = os.getenv('EMAIL_ACCOUNT')
auth_password = os.getenv('PASSWORD')
imap_server = os.getenv('IMAP_SERVER')
smtp_server = os.getenv('SMTP_SERVER')

# Lista de emails que devem ser automaticamente ignorados por qualquer motivo
trashcan_mails = os.getenv('TRASHCAN_EMAILS').split(',')


def find_useless_emails():
    mail = imaplib.IMAP4_SSL(imap_server)
    mail.login(email, auth_password)
    mail.select('inbox')

    status, messages = mail.search(None, 'ALL')

    if status != 'OK':
        print('Failed to find messages.')
        return
    
    email_ids = messages[0].decode().split()

    for email_id in email_ids:
        status, data = mail.fetch(email_id, '(RFC822)')

        print(data)

        # if status != 'OK':
        #     print(f'Error fetching email with ID{email_id}')


find_useless_emails()