import json
import logging

from django.urls import reverse
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.sessions.models import Session
from django.core.serializers.json import DjangoJSONEncoder
from rest_framework.decorators import api_view
from rest_framework import status
from API.models import UserInfo, Bookmarks, Bookmark, Bookmark_Of_Customer

logger = logging.getLogger(__name__)

@api_view(['GET'])
def index(request):
    if request.method == 'GET':
    
        host_url = request.get_host()
        redirect_url = reverse('API:get_my_data')
        full_redirect_url = f"http://{host_url}{redirect_url}"
        
        try: 
            if request.session['update']:
                request.session['update'] = False
                
                user_bookmark = request.session['my_data']  # response 형식의 데이터를 return
                user_bookmark_json = json.dumps(user_bookmark, cls=DjangoJSONEncoder)
                customer_id = request.session['customer_id']
                context = {
                    'user_bookmark_json': user_bookmark_json,
                    'customer_id': customer_id,
                }
                
                return render(request, 'SERVICE/index.html', context) 
            
            else:
                return redirect(full_redirect_url)
            
        except KeyError:
            return redirect(full_redirect_url)
    
    else:
        logger.error("[ERROR] Illegal request is requested.")
        return JsonResponse({'success': False}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['POST'])
def user_info(request):
    if request.method == 'POST':
        print("GET in user_info requested!")
        data = json.loads(request.body.decode('utf-8'))
        
        suser_id = data['customer_id']
        suser_email = data['userEmail']
        request.session['customer_id'] = data['customer_id']
        request.session['userEmail'] = data['userEmail']
        
        print(suser_id, suser_email)
        
        return JsonResponse({'success': True})
    

@api_view(['POST', 'GET'])
def search_tags(request):
    # new tab에서 검색하고자 하는 키워드에 대한 함수
    if request.method == 'POST':
        # input 처리
        input_data = request.POST.get('tag')
        print("User request, tag: ", input_data)
        
        # 0. 유저 정보 획득
        # 1. 해당 유저의 북마크만 검색
        # 2. 입력된 값을 타이틀, 태그에서 검색
        # 3. 결과 출력
        
        # 유저 정보 획득: 새 탭이 열릴때 획득.
        
        ####
        # input_data split
        input_tags = [tag.strip() for tag in input_data.split(',') if tag.strip()]
        print("input_tags: ", input_tags)
        # 유저 북마크 정보만 검색
        suser = Bookmark_Of_Customer.objects.filter(customer_id=request.session['customer_id'])
        
        # 이제 여기서 북마크 정보들을 가지고, Bookmark에서 필터링이 필요.
        suser_bookmark = Bookmark.objects.filter(no__in=suser)
        suser_bookmark_with_tags = suser_bookmark.filter(tags__icontains=input_tags[0])

        print("suser: ", suser)
        print("suser_bookmark: ", suser_bookmark)
        print("suser_bookmark_with_tags: ", suser_bookmark_with_tags)
        
        return_url = [[item.url] for item in suser_bookmark_with_tags]
        return_tags = [[item.tags] for item in suser_bookmark_with_tags]
        print("tags: ", return_tags)
        filtered_data = {item.url:item.tags for item in suser_bookmark_with_tags}

        print("filtered_data: ", filtered_data)
        
        return render(request, 'test_for_search.html', {'filtered_data': filtered_data})
        # return JsonResponse({'success': True}, status=200)
    
    # new tab을 띄우라는 크롬 익스텐션의 요청에 따른 함수
    elif request.method == 'GET':
        print("get is requested!")
        # Handle the GET request
        # Add any necessary logic or processing here
        
        # Return a response
        response_data = {'message': 'This is a GET request'}
        return render(request, 'test_for_search.html')
    
    else:
        return JsonResponse(status=400)