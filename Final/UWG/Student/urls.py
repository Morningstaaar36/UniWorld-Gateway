from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name="StudentHome"),
    path('<str:username>/search_reports_rendererer/', views.search_reports_rendererer, name="search_reports_rendererer"),
    path('<str:username>/search_reports_by_year/', views.search_reports_by_year, name="search_reports_by_year"),
    path('<str:username>/Application/', include('Application.urls')),
    path('<str:username>/Profile/', include('Profile.urls')),
    path('<str:username>/Publication/', include('Publication.urls')),
    path('<str:username>/Documents/', include('Documents.urls')),
]

