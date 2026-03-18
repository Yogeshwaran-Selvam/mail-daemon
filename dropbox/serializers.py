from rest_framework import serializers
from .models import EmailMessage

class EmailMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailMessage
        fields = '__all__' # This tells DRF to convert every column in the table to JSON