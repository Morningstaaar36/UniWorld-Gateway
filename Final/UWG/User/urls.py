from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="UserHome"),
    path('signin/', views.signin, name="UserSignin"),
    path('signup/', views.signup, name="UserSignup"),
]
