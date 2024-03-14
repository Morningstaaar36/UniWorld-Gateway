from django.contrib import admin
from django.urls import path, include
from . import views
urlpatterns = [
path('', views.publication_by_username, name="publication_home_by_username"),
path('updatePublicationRenderer/', views.updatePublicationRenderer, name='updatePublicationRenderer'),
path('deletePublication/', views.deletePublication, name='deletePublication'),
path('addPublicationRenderer/', views.addPublicationRenderer, name='addPublicationRenderer'),
path('addPublication/',views.addPublication,name='addPublication'),
path('updaterPublication/', views.updaterPublication, name='updaterPublication'),

]