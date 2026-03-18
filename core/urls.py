from django.contrib import admin
from django.urls import path
from django.http import HttpResponse
# Import all your views
from dropbox.views import trigger_fetch, get_emails, delete_email, web_dashboard, web_archive_email 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('favicon.ico', lambda request: HttpResponse(status=204)), 
    
    # --- WEB UI URLS ---
    path('', web_dashboard, name='web-dashboard'), # The homepage!
    path('archive/<int:pk>/', web_archive_email, name='web-archive'),
    
    # --- API URLS ---
    path('api/run-fetcher/', trigger_fetch, name='run-fetcher'),
    path('api/emails/', get_emails, name='get-emails'),
    path('api/emails/<int:pk>/', delete_email, name='delete-email'),
]