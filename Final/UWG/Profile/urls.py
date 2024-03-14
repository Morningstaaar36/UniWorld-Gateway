from django.urls import path
from . import views

urlpatterns = [
    path('', views.profile_by_username, name='profile_home_by_username'),
    path('updateProfileRenderer/',views.updateProfileRenderer,name='updateProfileRenderer'),
    path('updateProfile/',views.updateProfile,name='updateProfile'),
    # Add more paths as needed
]
