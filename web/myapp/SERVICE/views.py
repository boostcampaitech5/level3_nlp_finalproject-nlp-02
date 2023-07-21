import json
from django.shortcuts import render
from django.http import HttpResponse
from django.core.serializers.json import DjangoJSONEncoder

def index(request):
    user_bookmark = request.session['my_data']  # response 형식의 데이터를 return
    user_bookmark_json = json.dumps(user_bookmark, cls=DjangoJSONEncoder)

    return render(request, 'SERVICE/index.html', {'user_bookmark_json': user_bookmark_json})
