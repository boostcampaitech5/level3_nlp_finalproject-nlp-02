from django.shortcuts import render
from django.http import HttpResponse


def index(request):
    user_bookmark = request.session['my_data'] # response 형식의 데이터를 return

    return render(request, 'html/index.html', {'user_bookmark': user_bookmark})