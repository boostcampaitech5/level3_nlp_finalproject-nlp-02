from django.urls import path, include

from . import views

app_name = 'SERVICE'
urlpatterns = [
    path('', views.index, name='index'),
]