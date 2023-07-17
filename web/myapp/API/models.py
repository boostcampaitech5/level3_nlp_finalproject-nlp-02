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
    업데이트 예정
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
    업데이트 예정
    '''
    no          = models.AutoField(primary_key=True)
    url         = models.URLField(max_length=300)
    title       = models.CharField(max_length=50)
    tags        = models.TextField()
    content     = models.TextField()
    summarize   = models.TextField(blank=True, null=True)
    reference   = models.CharField(max_length=50)
    topic       = models.CharField(max_length=50, blank=True, null=True)
    create_date = models.DateTimeField(auto_now_add=True)
    update_date = models.DateTimeField(auto_now=True)

# 유저의 북마크 저장 정보
class Bookmark_Of_Customer(models.Model):
    '''
    업데이트 예정
    '''
    customer_id         = models.CharField(max_length=50, primary_key=True)
    bookmark_no         = models.AutoField(primary_key=True)
    tags                = models.TextField()
    name                = models.CharField(max_length=50)
    create_date         = models.DateTimeField(auto_now_add=True)
    update_date         = models.DateTimeField(auto_now=True)
    save_path_at_chrome = models.CharField(max_length=100)
    save_path_at_ours   = models.CharField(max_length=100)