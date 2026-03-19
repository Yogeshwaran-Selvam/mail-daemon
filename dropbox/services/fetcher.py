import imaplib
import re
from email import message_from_bytes
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
        
        gmail_hash_id = ""
        subject = "(No Subject)"
        sender = "Unknown"
        body = ""
        
        try:
            res, msg_data = mail.fetch(e_id, '(RFC822 X-GM-THRID)')
            
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    # 1. Extract the Gmail Hash ID from the metadata (response_part[0])
                    metadata = response_part[0].decode()
                    thrid_match = re.search(r'X-GM-THRID\s+(\d+)', metadata)
                    if thrid_match:
                        try:
                            decimal_id = int(thrid_match.group(1))
                            gmail_hash_id = hex(decimal_id)[2:] 
                        except:
                            gmail_hash_id = ""
                    # 2. Parse the actual email content (response_part[1])
                    msg = email.message_from_bytes(response_part[1])
                    
                    # Subject Decoding
                    subj_header = msg.get("Subject")
                    if subj_header:
                        decoded = decode_header(subj_header)[0]
                        subject, encoding = decoded
                        if isinstance(subject, bytes):
                            subject = subject.decode(encoding if encoding else "utf-8", errors="ignore")
                    
                    sender = msg.get("From", "Unknown")
                    
                    print(gmail_hash_id, sender)
                    
                    # Body Extraction
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == "text/plain" and "attachment" not in str(part.get("Content-Disposition")):
                                payload = part.get_payload(decode=True)
                                if payload:
                                    body = payload.decode(errors="ignore")
                                    break # Take the first text part found
                    else:
                        payload = msg.get_payload(decode=True)
                        if payload:
                            body = payload.decode(errors="ignore")

            # --- CRITICAL: Append OUTSIDE the response_part loop, but INSIDE the e_id loop ---
            print(gmail_hash_id)
            extracted_emails.append({
                "id": e_id.decode(),
                "gmail_hash": gmail_hash_id,
                "subject": subject,
                "sender": sender,
                "body": body[:2000]
            })
                    
        except Exception as e:
            print(f"⚠️ Error processing email {e_id.decode()}: {e}")
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