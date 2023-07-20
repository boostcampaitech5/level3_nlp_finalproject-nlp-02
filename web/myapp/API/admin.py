from django.contrib import admin
from .models import UserInfo, Bookmarks

# Register your models here.
admin.site.register(UserInfo)
admin.site.register(Bookmarks)