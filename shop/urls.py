from django.urls import path
from django.conf.urls import url
from . import views
from .views import Home, MyPage, Login, LogOut, Content, Write, PostPage, PostsView

app_name = 'shop'
urlpatterns = [
    path('home', Home.as_view(), name="posts"),
    path('mypage', MyPage.as_view()),
    path('login', Login.as_view()),
    path('logout', LogOut.as_view()),
    path('write', Write.as_view()),
    path('content', Content.as_view(), name="content"),
    path('post', PostsView.as_view(), name="posts"),
    # path('home', PostsView.as_view(), name="posts"),
    url(r'^sign$', views.sign, name='sign'),
]
