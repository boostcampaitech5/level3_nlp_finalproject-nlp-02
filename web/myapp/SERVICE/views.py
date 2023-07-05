from django.shortcuts import render
from django.http import HttpResponse


def index(request):
    return HttpResponse("SERVICE 앱의 index 테스트 성공")