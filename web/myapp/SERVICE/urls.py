from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('google/login/', views.google_login, name='google_login'),
    path('google/callback', views.google_callback, name='google_callback'),
    path('accounts/', include('allauth.urls')),
]