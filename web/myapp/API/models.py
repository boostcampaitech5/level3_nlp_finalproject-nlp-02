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
    context = models.TextField()
    # date = models.DateTimeField(auto_now_add=True)
    folder = models.TextField()
    tag = models.TextField()
    # bookmarked_date = models.DateTimeField(blank=True, null=True)
    # tag = models.CharField(max_length=10)
        
    def __str__(self):
        return str(self.userId)