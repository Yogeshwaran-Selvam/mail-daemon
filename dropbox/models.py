from django.db import models

class EmailMessage(models.Model):
    # Pre-defined categories to keep the database organized
    CATEGORY_CHOICES = [
        ('Work', 'Work'),
        ('Alert', 'Alert'),
        ('Newsletter', 'Newsletter'),
        ('Personal', 'Personal'),
        ('Other', 'Other'),
    ]

    # Core Email Data
    message_id = models.CharField(max_length=255, unique=True)
    gmail_hash = models.CharField(max_length=100, blank=True, null=True)
    sender = models.CharField(max_length=255)
    subject = models.CharField(max_length=500)
    
    # AI Generated Data
    summary = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Other')
    action_required = models.BooleanField(default=False)
    
    # App State Data
    created_at = models.DateTimeField(auto_now_add=True) # Timestamps when it hit the DB

    def __str__(self):
        return f"[{self.category}] {self.subject} - {self.sender}"