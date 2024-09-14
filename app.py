import os
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
trashcan_mails = os.getenv('TRASHCAN_EMAILS').split(',')

def find_useless_emails():
    mail = imaplib.IMAP4_SSL(imap_server)
    mail.login(email_account, auth_password)
    mail.select('inbox')

    status, messages = mail.search(None, 'ALL')

    if status != 'OK':
        print('Failed to retrieve messages.')
        return
    
    email_ids = messages[0].decode().split()

    # Dividir em lote
    batch_size = 5
    total_size = len(email_ids)

    for i in range(0, 15, batch_size):
        email_batch = email_ids[i:i + batch_size]
        status, data = mail.fetch(email_id, '(RFC822)')
        raw_data = data[0][1]
        filtered_data = email.message_from_bytes(raw_data)
        sender = decode_header(filtered_data.get("from"))[0]

        if status != 'OK':
            print(f'Error fetching email with ID{email_id}')
            continue

        if sender not in trashcan_mails:
            print('No trashcan senders found. Good!')
        else: 
            print(f'Deleting emails from: {sender}')
            mail.store(email_id, '+FLAGS', '\\Deleted')

            

    mail.expunge()
    print(f'Processed batch {i // batch_size + 1} / {total_size // batch_size + 1}')

find_useless_emails()