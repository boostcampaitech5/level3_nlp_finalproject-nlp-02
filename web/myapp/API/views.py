from django.shortcuts import render
from django.http import HttpResponse


def index(request):
    return HttpResponse("API 앱의 index 테스트 성공")

def test_request(request):
    return render(request, 'html/test_request.html')

def test_response(request):
    db = {}

    db['id'] = request.GET['id']
    db['pwd'] = request.GET['pwd']

    return render(request, "html/test_response.html", db)

def inference(request):
    print(request.POST)

    return HttpResponse("성공적으로 받기")