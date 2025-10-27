from django.shortcuts import render
from django.http import HttpRequest

def index(request: HttpRequest):
    """Serve the single-page frontend container for Vue."""
    return render(request, "projects/index.html")
