import os
import sys
import json
import logging
import pickle

from django.urls import reverse
from django.shortcuts import render, redirect
from django.utils import timezone
from django.http import HttpResponse, JsonResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import UserInfo, Bookmarks, Customer, Bookmark, Bookmark_Of_Customer
from .utils import *
# from .serializers import PostSerializer

# 모델 시스템 path 추가
# print(os.path.dirname(__file__))
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
        
        flag, tags_result = save_single_bookmark(data)
        
        if flag:
            return JsonResponse({'success': True, 'tags_result': tags_result})
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
        
        for single_data in data:
            if single_data:
                flag, tags_result = save_single_bookmark(single_data)
                flag.append(flag)
        
        # flag = [save_single_bookmark(single_data) for single_data in data if single_data]

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
        return False, ""

    # 중복 저장 예외 시퀀스 추가
    dup_bookmark = Bookmark_Of_Customer.objects.filter(customer_id=data['customer_id']).filter(bookmark_no=url_no)
    
    if dup_bookmark:
        logger.info("User already saved same url: ", tags_result)
        return True, tags_result
    
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
    return True, tags_result


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
def get_my_data(request):
    '''
    Extensions에서 id와 email을 POST로 받아와
    처음 접속이라면 테이블 customer에 유저 정보를 저장하고
    해당 유저에 대한 bookmark 정보를 response로 보내줌
    '''
    if request.method == 'POST':
        """
            request: {'id': id, 'email': emai}
        """
        try:
            data = json.loads(request.body.decode('utf-8'))
            print("In get_my_data, Received: ", data)
            return JsonResponse({'message': 'User info received successfully'})
        except:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)

    
    if request.method == 'GET':
        """
            request: {'id': id, 'email': emai}
        """
        # data = json.loads(request.body.decode('utf-8'))

        # 처음 접속했다면 테이블 customer에 저장
        # code

        # 해당 유저에 대한 bookmark 정보 가져오기
        # table_bookmark_of_customer = Bookmark_Of_Customer.objects.filter(customer_id=data['id'])
        print("request id: ", request.GET['id'], type(request.GET['id']))
        table_bookmark_of_customer = Bookmark_Of_Customer.objects.filter(customer_id=request.GET['id']) # test
        table_bookmark = Bookmark.objects.filter(no__in=table_bookmark_of_customer)
        
        # 데이터를 리스트 data에 저장
        datas = []
        for bookmark_of_customer_row, bookmark_row  in zip(table_bookmark_of_customer, table_bookmark):
            data = {
                "bookmark_no": bookmark_row.no,
                "name": bookmark_of_customer_row.name, "tags": bookmark_of_customer_row.tags,
                "save_path_at_outs": bookmark_of_customer_row.save_path_at_ours,
                "url": bookmark_row.url, "summarize": bookmark_row.summarize, "topic": bookmark_row.topic,
            }

            datas.append(data)
        
        # dict to json
        # data_json = json.dumps({datas})
        # 세션에 bookmarks 데이터 저장
        request.session['my_data'] = datas
        request.session['customer_id'] = request.GET['id']
        
        host_url = request.get_host()
        redirect_url = reverse('SERVICE:index')
        full_redirect_url = f"http://{host_url}{redirect_url}"
        
        print("full_redirect_url: ", full_redirect_url)
        return redirect(full_redirect_url)
    else:
        raise Http404("Question does not exist") 


@api_view(['POST'])
def remove_bookmark(request):
    '''
    버튼이 눌린 데이터를 삭제한 후에 테이블 정보를 다시 불러오기
    '''
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        customer_id = data['customer_id']
        url = data['url']

        try:
            find_row = Bookmark_Of_Customer.objects.filter(customer_id=customer_id, url=url)[0]
            find_row.delete()
        except:
            pass
        
        datas = request.session['my_data']
        for idx, data in enumerate(datas):
            if data['url'] == url:
                del data # 삭제가 안 되면 datas.pop(idx)
                break

        request.session['my_data'] = datas
        request.session['customer_id'] = customer_id
        
        host_url = request.get_host()
        redirect_url = reverse('SERVICE:index')
        full_redirect_url = f"http://{host_url}{redirect_url}"
        
        print("full_redirect_url: ", full_redirect_url)
        return redirect(full_redirect_url)