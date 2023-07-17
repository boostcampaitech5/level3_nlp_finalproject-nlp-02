from django.conf import settings
from django.db import models
from django.utils import timezone

# Parent
class UserInfo(models.Model):
    userId = models.CharField(max_length=30)
    userEmail = models.CharField(max_length=40)
    userPassword = models.CharField(max_length=30)
    
    def __str__(self):
        return self.userId

# Child
class Bookmarks(models.Model):
    userNumber = models.ForeignKey('UserInfo', on_delete=models.CASCADE, db_column='userNumber')
    userId = models.CharField(max_length=30)
    userEmail = models.CharField(max_length=40)
    url = models.TextField()
    title = models.TextField(null=True, default='post title')       # url's post title
    bookmarkTitle = models.TextField(null=True, default=title)      # user defined
    content = models.TextField(null=True, default='')               # url's post content
    folderName = models.TextField(null=True)
    tag = models.TextField(null=True, default='Null')
    # date = models.DateTimeField(auto_now_add=True)
    # bookmarked_date = models.DateTimeField(blank=True, null=True)
        
    def __str__(self):
        return str(self.userId)
    
# 유저 정보
class Customer(models.Model):
    '''
    id          : Chrome Extensions에서 넘겨 받은 유저 ID (고유 키) 또는 랜덤값
    email       : Chrome Extensions에서 넘겨 받은 유저 Email 또는 우리의 홈페이지에서 가입시 입력한 Email
    pwd         : 비밀번호
    name        : 유저 이름
    birth       : 유저 생년월일
    create_date : Chrome Extensions을 통해 처음 접속한 날짜 또는 유저 계정 생성 날짜
    update_date : 유저 계정 정보가 최근 업데이트 된 날짜
    '''
    id          = models.CharField(max_length=50, primary_key=True)
    email       = models.EmailField(max_length=50, unique=True)
    pwd         = models.CharField(max_length=50)
    name        = models.CharField(max_length=10)
    birth       = models.DateField()
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

# 북마크 정보
class Bookmark(models.Model):
    '''
    no          = Auto Increment이기 때문에 북마크 저장 순서라고 볼 수 있는 no
    url         = 글 url
    title       = 글 원본 제목
    content     = 글 본문
    summarize   = 글 본문을 요약한 내용
    reference   = 글 url에서 플랫폼이 어딘지, ex) naver.com => naver, velog.io => velog
    topic       = 글 주제 또는 글 카테고리
    tags        = content를 자동 태깅한 결과
    create_date = 북마크 생성 날찌
    update_date = 북마크 최근 업데이트 날짜
    '''
    no          = models.AutoField(primary_key=True)
    url         = models.URLField(max_length=300)
    title       = models.CharField(max_length=50)
    content     = models.TextField()
    summarize   = models.TextField(blank=True, null=True)
    reference   = models.CharField(max_length=50)
    topic       = models.CharField(max_length=50, blank=True, null=True)
    tags        = models.TextField()
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

# 유저의 북마크 저장 정보
class Bookmark_Of_Customer(models.Model):
    '''
    customer_id         = Customer 테이블에 있는 id
    bookmark_no         = Bookmark 테이블에 있는 no
    tags                = default 값은 Bookmark.tags 이지만, 유저가 원하는 태그를 기입 가능
    name                = default 값은 Bookmark.title 이지만, 유저가 원하는 북마크명 기입 가능
    create_date         = 북마크 저장 날짜
    update_date         = 북마크 최근 업데이트 날짜
    save_path_at_chrome = 크롬에서 북마크가 저장되는 경로
    save_path_at_ours   = 우리 플랫폼에서 북마크가 저장되는 경로
    '''
    customer_id         = models.CharField(max_length=50, primary_key=True)
    bookmark_no         = models.AutoField(primary_key=True)
    tags                = models.TextField()
    name                = models.CharField(max_length=50)
    create_date         = models.DateTimeField(auto_now_add=True)
    update_date         = models.DateTimeField(auto_now=True)
    save_path_at_chrome = models.CharField(max_length=100)
    save_path_at_ours   = models.CharField(max_length=100)