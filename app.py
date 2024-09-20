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
trashmails = os.getenv('TRASHCAN_EMAILS')
regulated_trashmail_list = trashmails.split(',') 

# Função de regex para normalizar os dados de remetente dos email
def regulate_email(text):
    if isinstance(text, bytes):
        text = text.decode('utf-8', errors='ignore')
    match = re.search(r'<(.+?)>', text)
    if match:
        return match.group(1)
    return "ERROR DECODING EMAIL."

# Função para conectar o email
def email_connection():
    mail = imaplib.IMAP4_SSL(imap_server)
    login_account = mail.login(email_account, auth_password)
    if login_account:
        print(f'Login successfull! Current account: {email_account}')
    else:
        print(f'Failed to connect to email account: {email_account}')
    mail.select('inbox')
    return mail

def find_useless_emails():
    mail = email_connection()

    status, messages = mail.search(None, 'ALL')
    email_ids = messages[0].decode().split()
    total_emails = len(email_ids)
    trashsenders_list = []

    print(f"Searching trashmails in {total_emails} emails. This may take a while.")

    for email_id in reversed(email_ids):

        status, data = mail.fetch(email_id, '(RFC822)')

        if status != 'OK':
            print(f'Failed fetching email data from ID: {email_id}')
            continue

        raw_data = data[0][1]
        filtered_data = email.message_from_bytes(raw_data)
        sender = decode_header(filtered_data.get("From"))[0][0]
        decoded_sender = regulate_email(sender)

        if decoded_sender in regulated_trashmail_list:
            print(f'Sending {decoded_sender} to trash list. ')
            trashsenders_list.append({'email_id': email_id, 'sender': decoded_sender})
        
    if not trashsenders_list:
        print("No trashmail found. Good!")
    
    option = input(f"\n Total of: {len(trashsenders_list)} emails are trash. Here's your trashmail list: {trashsenders_list}. Make sure to confirm you did not insert any important email. \n Are you sure you want to procede? (Y/N)").lower()
        
    if option != 'y':
        print('Canceling operation.')
        return
    
    print(f'Trashmails deleted.')

find_useless_emails()