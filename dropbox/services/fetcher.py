import imaplib
import email
from email.header import decode_header
import os
from dotenv import load_dotenv

# Load the environment variables from your .env file
load_dotenv()

# Get credentials
USERNAME = os.getenv("EMAIL_USER")
PASSWORD = os.getenv("EMAIL_APP_PASSWORD")
IMAP_SERVER = os.getenv("EMAIL_HOST")

def fetch_unread_emails():
    """Connects to the inbox, fetches unread emails, and returns a list of dictionaries."""
    
    # 1. Connect to the server securely
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(USERNAME, PASSWORD)
    except Exception as e:
        print(f"Login failed: {e}")
        return []

    # 2. Select the inbox
    mail.select("inbox")

    # 3. Search for ALL unread emails
    status, messages = mail.search(None, '(UNSEEN)')
    
    if status != "OK":
        print("No unread emails found.")
        return []

    # Get the list of email IDs
    email_ids = messages[0].split()
    
    # 1. BATCH PROCESSING: Process 10 emails at a time to stay under Gemini's 15 req/min limit
    email_ids = email_ids[-20:] 
    
    extracted_emails = []

    # 4. Loop through the IDs and fetch the email data
    for e_id in email_ids:
        print(f"Downloading email ID {e_id.decode()}...")
        
        try:
            res, msg_data = mail.fetch(e_id, '(BODY.PEEK[])')
            
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding if encoding else "utf-8")
                    
                    sender = msg.get("From")
                    
                    body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == "text/plain" and "attachment" not in str(part.get("Content-Disposition")):
                                try:
                                    body = part.get_payload(decode=True).decode()
                                except:
                                    pass
                    else:
                        body = msg.get_payload(decode=True).decode()
                    
                    extracted_emails.append({
                        "id": e_id.decode(),
                        "subject": subject,
                        "sender": sender,
                        "body": body[:2000]
                    })
                    
        except Exception as e:
            print(f"⚠️ Failed to download email {e_id.decode()}. Error: {e}")
            # 2. GRACEFUL EXIT: If the connection dies, stop the loop immediately
            if "eof" in str(e).lower() or "socket" in str(e).lower() or "abort" in str(e).lower():
                print("🚨 Server closed connection early. Saving what we have...")
                break
            continue

    # 3. SAFE LOGOUT: Don't crash if the socket is already dead
    try:
        mail.logout()
    except Exception:
        pass 
        
    return extracted_emails

if __name__ == "__main__":
    print("Checking inbox...")
    mails = fetch_unread_emails()
    for m in mails:
        print(f"From: {m['sender']}")
        print(f"Subject: {m['subject']}\n")