from django.shortcuts import render
from django.http import HttpResponse


def index(request):
    return HttpResponse("Hello, World. You're at the polls index.")

def test(request):
    return render(request, 'html/test_form.html')

def inference(request):
    db = {}

    

    return render(request, "html/inference.html")