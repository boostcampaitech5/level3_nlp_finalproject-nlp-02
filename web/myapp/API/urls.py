from django.urls import path, include
from django.contrib import admin

from . import views

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('test_request/', views.test_request, name='test_request'),
    path('test_response/', views.test_response, name='test_response'),
    path('inference/', views.inference, name='inference'),
    path('post/', views.post_api, name='post'),
    path('get/', views.get_api, name='post'),
    path('post_history/', views.post_history, name='post_history')
]