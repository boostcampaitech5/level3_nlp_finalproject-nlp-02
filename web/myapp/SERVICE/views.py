import json

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from rest_framework.decorators import api_view
from API.models import UserInfo, Bookmarks
from django.contrib.sessions.models import Session


def index(request):
    return HttpResponse("SERVICE 앱의 index 테스트 성공")


@api_view(['POST'])
def user_info(request):
    if request.method == 'POST':
        print("GET in user_info requested!")
        data = json.loads(request.body.decode('utf-8'))
        
        suser_id = data['userId']
        suser_email = data['userEmail']
        request.session['userId'] = data['userId']
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
        
        # 유저 북마크 정보만 검색
        suser_bookmark = Bookmarks.objects.filter(userId=request.session['userId'])
        
        # title 및 태그 검색
        filtered_title = suser_bookmark.filter(title=input_data)
        filtered_tag = suser_bookmark.filter(tag=input_data)
        
        # 출력
        title_url_list = [value.url for value in filtered_title]
        tag_url_list = [value.url for value in filtered_tag]
        title_title_list = [value.bookmarkTitle for value in filtered_title]
        title_tag_list = [value.bookmarkTitle for value in filtered_tag]

        filtered_data = {
            'data': input_data,
            'url': title_url_list + tag_url_list,
            'title': title_title_list + title_tag_list,
        }
        
        return render(request, 'test_for_search.html', filtered_data)
    
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