from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('test_request/', views.test_request, name='test_request'),
    path('test_response/', views.test_response, name='test_response'),
    path('inference/', views.inference, name='inference'),
]