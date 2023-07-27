from django.urls import path, include
from django.contrib import admin

from . import views

app_name = 'API'
urlpatterns = [
    # path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('test_request/', views.test_request, name='test_request'),
    path('test_response/', views.test_response, name='test_response'),
    path('inference/', views.inference, name='inference'),
    path('post/', views.post_api, name='post'),
    path('get/', views.get_api, name='get'),
    path('post_history/', views.post_history, name='post_history'),
    path('get_my_data/', views.get_my_data, name='get_my_data'),
    path('test_create_data/', views.test_create_data, name='test_create_data'),
    path('tag_update', views.tag_update, name='tag_update'),
    path('remove_bookmark/', views.remove_bookmark, name='remove_bookmark'),
]