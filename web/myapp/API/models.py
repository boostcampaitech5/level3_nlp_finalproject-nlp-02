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
    userId = models.ForeignKey('UserInfo', on_delete=models.CASCADE, db_column='userId')
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