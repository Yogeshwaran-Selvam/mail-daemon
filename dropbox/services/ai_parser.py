import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

def summarize_emails_batch(emails_list):
    """Sends a batch of emails to Gemini and returns a list of JSON summaries."""
    if not emails_list:
        return []
        
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"
    
    # 1. Compile all emails into one massive text block
    email_text_block = ""
    for i, mail in enumerate(emails_list):
        email_text_block += f"--- EMAIL {i} ---\nSender: {mail['sender']}\nSubject: {mail['subject']}\nBody: {mail['body']}\n\n"
    
    # 2. Update the prompt to ask for an Array of Objects
    prompt = f"""
    You are an AI email assistant. Analyze the following batch of emails. 
    
    {email_text_block}
    
    Respond ONLY with a valid JSON ARRAY of objects. The order of objects MUST exactly match the order of the emails provided.
    Each object must match this exact structure:
    {{
        "summary": "A concise 2-sentence summary of the email.",
        "category": "Choose exactly one: [Work, Alert, Newsletter, Personal, Other]",
        "action_required": true or false
    }}
    """
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseMimeType": "application/json"}
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status() 
        result_text = response.json()['candidates'][0]['content']['parts'][0]['text']
        
        # Returns a Python LIST of dictionaries
        return json.loads(result_text)
        
    except Exception as e:
        print(f"⚠️ AI Batch Parsing failed. Error: {e}")
        # If it fails, return a list of 'Failed' objects so the DB still saves the raw emails
        return [{"summary": "Failed to generate summary.", "category": "Other", "action_required": False} for _ in emails_list]

# --- Quick Test Block ---
if __name__ == "__main__":
    print("Testing Gemini API...")
    test_res = summarize_emails_batch(
        "Security alert", 
        "no-reply@accounts.google.com", 
        "We noticed a new login from Arch Linux on your account. If this was you, you don't need to do anything."
    )
    print(json.dumps(test_res, indent=4))