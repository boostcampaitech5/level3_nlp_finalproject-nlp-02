from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('test_for_search/', views.search_tags, name='search_tags'),
    path('user_info/', views.user_info, name='user_info'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)