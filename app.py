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


# Função de regex para normalizar os dados de remetente dos email
def regulate_email(text):
    match = re.search(r'<(.+?)>', text)
    if match:
        return match.group(1)
    return None

# Função para conectar o email
def email_connection():
    global mail
    mail = imaplib.IMAP4_SSL(imap_server)
    mail.login(email_account, auth_password)
    print(f'Login successfull! Current account: {email_account}')
    mail.select('inbox')

def find_and_delete_useless_emails():

    # Variables
    senders_list = []

    status, messages = mail.search(None, 'ALL')

    if status != 'OK':
        print('Failed to access inbox.')
        return
    
    email_ids = messages[0].decode().split()

    for email_id in reversed(email_ids):

        status, data = mail.fetch(email_id, '(RFC822)')

        if status != 'OK':
            print(f'Failed fetching email data. Email ID: {email_id}')
            continue

        raw_data = data[0][1]
        filtered_data = email.message_from_bytes(raw_data)
        sender = decode_header(filtered_data.get("From"))[0][0]
        decoded_sender = regulate_email(sender)
        # print(decoded_sender) 

        #TODO: verificar a decodificação do sender, lembro que tinha uns que nao estavam corretamente normalizados

        if sender in trashmails_list:
            senders_list.append(sender) 
            mail.store(email_id, '+FLAGS', '\\Deleted')

            print(f'Deleting emails from: {senders_list}')
                
            option = input(f'Are you sure you want to procede? (Y/N)').lower()
                
            if option != 'y':
                print('Canceling deletion.')
                break

    print("No trashcan emails found. Good!")


email_connection()

find_and_delete_useless_emails()