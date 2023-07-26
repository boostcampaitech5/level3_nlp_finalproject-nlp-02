import json
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.core.serializers.json import DjangoJSONEncoder
from rest_framework.decorators import api_view

def index(request):
    user_bookmark = request.session['my_data']  # response 형식의 데이터를 return
    user_bookmark_json = json.dumps(user_bookmark, cls=DjangoJSONEncoder)
    customer_id = request.session['customer_id']

    context = {
        'user_bookmark_json': user_bookmark_json,
        'customer_id': customer_id,
    }
    
    return render(request, 'SERVICE/index.html', context)