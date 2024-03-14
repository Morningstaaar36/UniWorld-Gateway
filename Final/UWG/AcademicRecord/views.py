# views.py
from django.shortcuts import render
from django.http import HttpResponse

def index(request, username):
    return HttpResponse(f"Academic Record Home {username}")
