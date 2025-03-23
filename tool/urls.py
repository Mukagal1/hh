"""
URL configuration for tools project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('main/', views.main, name='main'),
    path('login/', views.login_view, name='login_view'),
    path('signup/', views.signup, name='signup'),
    path('signout/', views.signout, name='signout'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('skills/', views.skills, name='skills'),
    path('skills/add/', views.add_skill, name='add_skill'),
    path('tests/', views.tests, name='tests'),
    path('chats/', views.chats, name='chats'),
    path('chats/<int:chat_id>/', views.chat_detail, name='chat_detail'),
    path('chats/user/<int:user_id>/', views.chat_with_user, name='chat_with_user'),
    path('profiles/', views.profiles, name='users'),
    path('profiles/<str:username>/', views.user_detail, name='user_detail'),
    path('set_resume/', views.set_resume, name='set_resume'),
    path('search_candidates/', views.search_candidates, name='search_candidates'),
    # path('search_user/', views.search_user, name='search_user'),
    # path('test/<int:test_id>/', views.tests, name='test'),
]