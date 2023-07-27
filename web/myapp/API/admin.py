from django.contrib import admin
from .models import UserInfo, Bookmarks, Customer, Bookmark, Bookmark_Of_Customer

# Register your models here.
# admin.site.register(UserInfo)
# admin.site.register(Bookmarks)
admin.site.register(Customer)
admin.site.register(Bookmark)
admin.site.register(Bookmark_Of_Customer)