"""Check admin@agentdeploy.info inbox via IMAP"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import imaplib
import email
from email.header import decode_header
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

USER = os.getenv('GMAIL_USER')
PASS = os.getenv('GMAIL_APP_PASSWORD')

def check_inbox(limit=10):
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.login(USER, PASS)
    mail.select('inbox')
    
    status, messages = mail.search(None, 'ALL')
    msg_ids = messages[0].split()
    
    if not msg_ids:
        print("Inbox is empty.")
        mail.logout()
        return []
    
    results = []
    for mid in msg_ids[-limit:]:
        status, data = mail.fetch(mid, '(RFC822)')
        msg = email.message_from_bytes(data[0][1])
        
        subject = decode_header(msg['Subject'])[0]
        subject = subject[0].decode(subject[1] or 'utf-8') if isinstance(subject[0], bytes) else subject[0]
        
        from_ = msg.get('From', '')
        date = msg.get('Date', '')
        
        body = ''
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == 'text/plain':
                    body = part.get_payload(decode=True).decode('utf-8', errors='replace')
                    break
        else:
            body = msg.get_payload(decode=True).decode('utf-8', errors='replace')
        
        results.append({
            'from': from_,
            'subject': subject or '(no subject)',
            'date': date,
            'body': body[:500]
        })
        
        print(f"From: {from_}")
        print(f"Subject: {subject}")
        print(f"Date: {date}")
        print(f"Preview: {body[:200]}")
        print("---")
    
    mail.logout()
    print(f"\nTotal: {len(msg_ids)} emails in inbox")
    return results

if __name__ == '__main__':
    check_inbox()
