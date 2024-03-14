from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.documents_home_by_username, name="documents_home_by_username"),
    path('add_document/', views.add_document, name='add_document'),  # Define the add_document URL pattern
    path('see_documents/', views.see_documents, name='see_documents'),  # Define the see_documents URL pattern
    path('manage_documents/', views.manage_documents, name='manage_documents'),  # Define the manage_documents URL pattern
    path('add_document_analyze/', views.add_document_analyze, name='add_document_analyze'),  # Define the add_document URL pattern
    path('see_documents_analyze/', views.see_documents_analyze, name='see_documents_analyze'),  # Define the see_documents URL pattern
    path('manage_documents_analyze/', views.manage_documents_analyze, name='manage_documents_analyze'),
    # Define the manage_documents URL pattern

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
