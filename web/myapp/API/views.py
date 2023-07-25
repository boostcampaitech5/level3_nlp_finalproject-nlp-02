import os
import sys
import json
import logging

from django.shortcuts import render
from django.utils import timezone
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import UserInfo, Bookmarks, Bookmark, Bookmark_Of_Customer
from .utils import *
# from .serializers import PostSerializer

# 모델 시스템 path 추가
print(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), "../../../"))
from model.tag_inference import TagModel, tag_model_instance
from model.test_tagging_model import get_tag_from_model

# 항상 먼저 켜져있어야 하는 변수
logger = logging.getLogger(__name__)
tag_model = tag_model_instance
logger.info("\nTagging model successfully initialized!\n")

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
            content = data['content']
            topics = None
            summarized = None

            # 여기에서 title과 id를 원하는 방식으로 저장하면 됩니다.
            print("== data")
            print(data)
            print("== title")
            print(title)
            print("== content")
            print(content)
            print("== Start Inferencing...")
            
            # TagModel = TagModel(title = title, content = content)
            # tags_result = TagModel.inference()

            return JsonResponse({'success': True})
        except KeyError:
            return JsonResponse({'success': False, 'error': 'Invalid data'})


# 단일 user bookmark 정보 송신 및 DB 저장
@api_view(['POST'])
def post_api(request):
    """
    Note:
        1. 기존 북마크 table search
        2. 없으면 북마크 table에 추가
        3. Bookmark_of_user 에 id 추가, bookmark no는 기존에 있었다면 search 한 결과, 없었다면 추가한 no.
        4. 중복 저장 시퀀스 예외처리
    """
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        # logger.info("\ndata: %s, %s", data, type(data))
        
        flag = save_single_bookmark(data)
        
        if flag:
            return JsonResponse({'success': True})
        else:
            return Response({'success': False}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    else:
        logger.error("[ERROR] Illegal request is requested.")
        return JsonResponse({'success': False}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


# user bookmark history 정보 송신 및 DB 저장
@api_view(['POST'])
def post_history(request):
    """
    Note:
        1. 리스트로 전달되는 북마크 히스토리 중 북마크 DB에 저장되지 않은 url 탐색 후 저장
        2. 해당 유저의 Bookmark_Of_Customer 업데이트
        3. 마찬가지로 중복 북마크 예외처리
    """
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        flag = []
        # logger.info("post_history requested!")
        
        flag = [save_single_bookmark(single_data) for single_data in data if single_data]

        if all(flag):
            return JsonResponse({'success': True})
        else:
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
    

def save_single_bookmark(data):
    """
    Note:
        단일 북마크 정보를 저장합니다. (Bookmark, Bookmark_Of_Customer)
        'def post_api(request)' 의 Note 동작 시퀀스의 구현입니다.
         
    Args:
        data: dict 형태로 들어오며, Bookmark와 Bookmark_Of_Customer에 저장할 내용들을 고루 가지고 있습니다.
    """
    # 기존 북마크 table search
    url_result = Bookmark.objects.filter(url=data['url'])
    try:
        url_no = url_result[0].no
        tags_result = url_result[0].tags
        
    except (AttributeError, IndexError) as e:
        # 없으면 북마크 table에 추가
        new_bookmark_info = {
            'url': data['url'],
            'title': data['title'],
            'content': data['content'],
            'summarize': "",
            'reference': "",
            'topic': "",
            'tags': "", # get_tag_from_model(data['content']),
            # 'create_date': ,
            # 'update_date': ,
        }
        
        # 모델로부터 tag 추론하기
        # tagModel = TagModel(title = data['title'], content = data['content'])
        tag_model.title = data['title']
        tag_model.content = data['content']
        
        tags_result = tag_model.inference()
        new_bookmark_info['tags'] = tags_result
        print("Tag result of bookmark page: ", tags_result)
        
        Bookmark.objects.create(**new_bookmark_info)
        url_no = Bookmark.objects.filter(url=data['url'])[0].no
    
    # 기타 오류
    except Exception as e:
        logger.exception("[Exception] Unexpected error occurred while saving the bookmark.")
        return False

    # 중복 저장 예외 시퀀스 추가
    dup_bookmark = Bookmark_Of_Customer.objects.filter(customer_id=data['customer_id']).filter(bookmark_no=url_no)
    
    if dup_bookmark:
        logger.exception("[Exception] User already saved same url.")
        return True
    
    # Bookmark_of_user에 id 추가
    new_bookmark_of_customer_info = {
        'customer_id': data['customer_id'],
        'bookmark_no': url_no,
        'tags': tags_result,
        'name': "",
        # 'create_date': "",
        # 'update_date': "",
        'save_path_at_chrome': "",
        'save_path_at_ours': "" ,
    }
    
    Bookmark_Of_Customer.objects.create(**new_bookmark_of_customer_info)
    return True


@api_view(['POST'])
def tag_update(request):
    '''
    웹 페이지에서 새롭게 갱신되는 태그 데이터를 업데이트합니다.
    
    request 형태:
        'customer id', 'bookmark no', 'tags(변경된 태그)'    
    '''
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))     # string type으로 전달된다.
        customer_id = data['customer_id']
        bookmark_no = data['bookmark_no']
        new_tags = ", ".join(data['new_tags'])
        
        print("Request in tag_update: ", data, type(data))
        
        # 업데이트
        target_row = Bookmark_Of_Customer.objects.filter(customer_id=customer_id).filter(bookmark_no=bookmark_no)
        target_row.update(tags=new_tags)
        
        return JsonResponse({'success': True})
    
    else:
        logger.error("[ERROR] Illegal request is requested.")
        return JsonResponse({'success': False}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        