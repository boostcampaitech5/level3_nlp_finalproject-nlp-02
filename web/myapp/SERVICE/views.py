from django.shortcuts import render
from django.http import HttpResponse


def index(request):
    return HttpResponse("SERVICE 앱의 index 테스트 성공")


def google_login(request):
    return HttpResponse("SERVICE 앱의 login 테스트 성공")


def google_callback(request):
    return HttpResponse("SERVICE 앱의 login callback 테스트 성공")