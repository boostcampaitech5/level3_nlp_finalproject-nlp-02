import os
import sys
import json
import logging
import pickle

from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import Customer, Bookmark, Bookmark_Of_Customer
from .utils import *
# from .serializers import PostSerializer

# dl_model_path = '../../model/models/'

# sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'model'))

# from models.tagging_model import get_tag_from_model

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

        except ObjectDoesNotExist:
            logger.info("[ERROR] Object Does Not Exist. DB will save userInfo first...")
            
            # 새로운 유저 정보 업데이트
            newUser = {'userId': data['userId'],
                       'userEmail': data['userEmail'],
                       'userPassword': '',
                       }
            UserInfo.objects.create(**newUser)
            
            logger.info("DB updates new userInfo.")
        
        # 기타 오류
        except Exception as e:
            logger.exception("[Exception] Unexpected error occurred while saving the bookmark.")
            return Response({'success': False}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Foreign key 재 업데이트
        data['userNumber'] = UserInfo.objects.get(userId=data['userId'])
        
        # 딥러닝 모델로부터 태그 정보 inference
        # tags = get_tag_from_model(data['content'])
        # data['tag'] = tags  # sample tag for now
        
        # 북마크 정보 저장
        Bookmarks.objects.create(**data)
        return JsonResponse({'success': True})
        
    else:
        logger.error("[ERROR] Illegal request is requested.")
        return JsonResponse({'success': False}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


# user bookmark history 정보 송신 및 DB 저장
@api_view(['POST'])
def post_history(request):
    if request.method == 'POST':
        
        data = json.loads(request.body.decode('utf-8'))
        print("post_history requested!")
        
        try:
            data[0]['userNumber'] = UserInfo.objects.get(userId=data[0]['userId'])  # bulk 이니까, 첫 데이터로 try.

        except ObjectDoesNotExist:
            logger.info("[ERROR] Object Does Not Exist. DB will save userInfo first...")
            
            # 새로운 유저 정보 업데이트
            newUser = {'userId': data[0]['userId'],
                       'userEmail': data[0]['userEmail'],
                       'userPassword': '',
                       }
            UserInfo.objects.create(**newUser)
        
        # bulk 처리.
        for bookmark_data in data:
            try:
                bookmark_data['userNumber'] = UserInfo.objects.get(userId=bookmark_data['userId'])
            except:
                pass    # undefined 인 경우는 pass.
        logger.info("DB updates new userInfo.")
        
        # 북마크 정보 저장
        bookmark_objects = [Bookmarks(**bookmark_data) for bookmark_data in data if bookmark_data]
        Bookmarks.objects.bulk_create(bookmark_objects)
        
        return JsonResponse({'success': True})

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

def test_create_data(request):
    customer_columns = ["id", "email", "pwd", "name", "birth"]

    # 북마크 샘플 데이터 생성
    bookmark_columns = ["url", "title", "content", "summarize", "reference", "topic", "tags"]
    bookmark_sample = [
        ['http://test1.com', '테스트1', '테스트1', '테스트1', '네이버', '테스트 데이터', '테스트, 테스트, 테스트, 테스트, 테스트'],
        ['http://test2.com', '테스트2', '테스트2', '테스트2', '네이버', '테스트 데이터', '테스트, 테스트, 테스트, 테스트, 테스트'],
        ['http://test3.com', '테스트3', '테스트3', '테스트3', '네이버', '테스트 데이터', '테스트, 테스트, 테스트, 테스트, 테스트'],
        ['http://test4.com', '테스트4', '테스트4', '테스트4', '네이버', '테스트 데이터', '테스트, 테스트, 테스트, 테스트, 테스트'],
        ['http://test5.com', '테스트5', '테스트5', '테스트5', '네이버', '테스트 데이터', '테스트, 테스트, 테스트, 테스트, 테스트'],
    ]
    for row in range(len(bookmark_sample)):
        sample = {
            bookmark_columns[idx]: bookmark_sample[row][idx] for idx in range(len(bookmark_columns))
        }
        Bookmark.objects.create(**sample)
    
    # 유저별 북마크 샘플 데이터 생성
    bookmark_of_cusomter_columns = ["customer_id", "bookmark_no", "tags", "name", "save_path_at_chrome", "save_path_at_ours"]
    bookmark_of_cusomter_sample = [
        ["114044069688253754526", 1, bookmark_sample[1][6], bookmark_sample[1][1], '', ''],
        ["114044069688253754526", 3, bookmark_sample[2][6], bookmark_sample[2][1], '', ''],
        ["114044069688253754526", 5, bookmark_sample[4][6], bookmark_sample[4][1], '', ''],
    ]
    for row in range(len(bookmark_of_cusomter_sample)):
        sample = {
            bookmark_of_cusomter_columns[idx]: bookmark_of_cusomter_sample[row][idx] for idx in range(len(bookmark_of_cusomter_columns))
        }
        Bookmark_Of_Customer.objects.create(**sample)

    return HttpResponse("데이터 생성 완료")

@api_view(['POST', 'GET'])
def get_my_date(request):
    '''
    Extensions에서 id와 email을 POST로 받아와
    처음 접속이라면 테이블 customer에 유저 정보를 저장하고
    해당 유저에 대한 bookmark 정보를 response로 보내줌
    '''
    if request.method == 'GET':
        # data = json.loads(request.body.decode('utf-8'))

        # 처음 접속했다면 테이블 customer에 저장
        # code

        # 해당 유저에 대한 bookmark 정보 가져오기
        # table_bookmark_of_customer = Bookmark_Of_Customer.objects.filter(customer_id=data['id'])
        table_bookmark_of_customer = Bookmark_Of_Customer.objects.filter(customer_id=request.GET['id']) # test
        talbe_bookmark = Bookmark.objects.filter(no__in=table_bookmark_of_customer)
        
        # 데이터를 리스트 data에 저장
        datas = []
        for bookmark_of_customer_row, bookmark_row  in zip(table_bookmark_of_customer, talbe_bookmark):
            data = {
                "name": bookmark_of_customer_row.name, "tags": bookmark_of_customer_row.tags,
                "save_path_at_outs": bookmark_of_customer_row.save_path_at_ours,
                "url": bookmark_row.url, "summarize": bookmark_row.summarize, "topic": bookmark_row.topic,
            }

            datas.append(data)
        
        # dict to json
        # data_json = json.dumps({datas})
        # 세션에 bookmarks 데이터 저장
        request.session['my_data'] = datas

        return redirect('http://nlp02.duckdns.org:30006/SERVICE/')
    else:
        raise Http404("Question does not exist") 