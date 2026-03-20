from django.http import JsonResponse
from .models import EmailMessage
from .services.fetcher import fetch_unread_emails
from .services.ai_parser import summarize_emails_batch
from .services.gmail_api import get_gmail_service
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import EmailMessageSerializer
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

def trigger_fetch(request):
    """The master function that fetches, summarizes, and saves emails."""
    print("Starting background fetch...")
    fetched_emails = fetch_unread_emails()
    
    # 1. Filter out emails we already have in the database FIRST
    emails_to_process = []
    for mail in fetched_emails:
        if EmailMessage.objects.filter(message_id=mail['id']).exists():
            print(f"Skipping {mail['id']} - Already exists.")
        else:
            emails_to_process.append(mail)
            
    if not emails_to_process:
        return JsonResponse({"status": "success", "message": "No new emails to process."})

    print(f"Processing {len(emails_to_process)} emails with Gemini AI in ONE batch...")
    
    # 2. Get all AI Summaries in a single API call
    ai_results = summarize_emails_batch(emails_to_process)
    
    processed_count = 0
    
    # 3. Zip the raw emails and the AI results together and save them
    if len(ai_results) == len(emails_to_process):
        for mail, ai_data in zip(emails_to_process, ai_results):
            EmailMessage.objects.create(
                message_id=mail['id'],
                gmail_hash=mail['gmail_hash'],
                sender=mail['sender'],
                subject=mail['subject'],
                summary=ai_data.get('summary', 'Failed to generate summary.'),
                category=ai_data.get('category', 'Other'),
                action_required=ai_data.get('action_required', False)
            )
            processed_count += 1
    else:
        print("🚨 Error: AI returned a different number of summaries than requested!")

    return JsonResponse({
        "status": "success", 
        "emails_processed": processed_count
    })

# --- WEB DASHBOARD VIEWS ---
def web_dashboard(request):
    """Renders the HTML dashboard with active emails."""
    # Fetch all emails that haven't been archived, newest first
    emails = EmailMessage.objects.order_by('-created_at')
    
    # Pass the emails into the HTML template
    return render(request, 'dashboard.html', {'emails': emails})

def web_archive_email(request, pk):
    """Archives an email in Gmail AND deletes it from the local web UI."""
    if request.method == "POST":
        # 1. Grab the email from the database BEFORE deleting it
        email = get_object_or_404(EmailMessage, pk=pk)
        gmail_id = email.gmail_hash
        
        # 2. Tell Google to archive it
        if gmail_id:
            try:
                service = get_gmail_service()
                if service:
                    # Remove the INBOX label to archive it in Gmail
                    service.users().messages().modify(
                        userId='me', 
                        id=gmail_id, 
                        body={'removeLabelIds': ['INBOX']}
                    ).execute()
                    print(f"Successfully archived {gmail_id} in Gmail!")
            except Exception as e:
                print(f"Failed to archive in Gmail: {e}")

        # 3. Delete it from the Django dashboard
        email.delete()
        
    return redirect('web-dashboard')

@api_view(['GET'])
def get_emails(request):
    """Returns a JSON list of all active emails, newest first."""
    # Fetch all emails that haven't been deleted
    emails = EmailMessage.objects.order_by('-created_at')
    
    # Convert them to JSON
    serializer = EmailMessageSerializer(emails, many=True)
    return Response(serializer.data)
