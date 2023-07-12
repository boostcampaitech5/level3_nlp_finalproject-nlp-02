import json
import logging

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import UserInfo, Bookmarks
from .utils import *
from .serializers import PostSerializer

logger = logging.getLogger(__name__)

def index(request):
    return HttpResponse("API 앱의 index 테스트 성공")

def test_request(request):
    return render(request, 'html/test_request.html')

def test_response(request):
    db = {}
    
    db['id'] = request.GET['id']
    db['pwd'] = request.GET['pwd']

    print(request)
    print(request.GET)
    print(request.POST)

    return render(request, "html/test_response.html", db)

@csrf_exempt
def inference(request):
    if request.method == 'PATCH':
        try:
            data = json.loads(request.body.decode('utf-8'))
            title = data['title']

            # 여기에서 title과 id를 원하는 방식으로 저장하면 됩니다.
            print("== data")
            print(data)
            print("== title")
            print(title)

            return JsonResponse({'success': True})
        except KeyError:
            return JsonResponse({'success': False, 'error': 'Invalid data'})


@api_view(['POST'])
def post_api(request):
    if request.method == 'POST':
        
        data = json.loads(request.body.decode('utf-8'))
        # logger.info("\ndata: %s, %s", data, type(data))
        
        try:
            data['userNumber'] = UserInfo.objects.get(userId=data['userId'])
            Bookmarks.objects.create(**data)
            return JsonResponse({'success': True})
        
        except ObjectDoesNotExist:
            logger.info("[ERROR] Object Does Not Exist. DB will save userInfo first...")
            
            # 새로운 유저 정보 업데이트
            newUser = {'userId': data['userId'],
                       'userEmail': data['userEmail'],
                       'userPassword': '',
                       }
            UserInfo.objects.create(**newUser)
            
            # 북마크 정보 재 저장
            data['userNumber'] = UserInfo.objects.get(userId=data['userId'])
            Bookmarks.objects.create(**data)
            
            logger.info("DB updates new userInfo with bookmark.")
            return JsonResponse({'success': True})
        
        # 기타 오류
        except Exception as e:
            logger.exception("[Exception] Unexpected error occurred while saving the bookmark.")
            return Response({'success': False}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    else:
        logger.error("[ERROR] Illegal request is requested.")
        return JsonResponse({'success': False}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['GET'])
def get_api(request):
    logger.info("GET requested!")
    bookmarked = Bookmarks.objects.all()    
    logger.info("answer: ", bookmarked)
    
    return JsonResponse({'sucess': True, 'data': 'its from server'})
    # return HttpResponse("get 호출됨")
