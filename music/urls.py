from django.urls import path
from . import views
urlpatterns = [
    path('' , views.home , name="home"),
    path('login/' , views.login_page , name="login"),
    path('signup/' , views.signup_page , name="signup"),
    path('logout/' , views.logout_page , name="logout"),
    path('profile/<str:pk>' , views.profile , name="profile"),
    path('music_player/<str:pk>' , views.music_player , name="music_player"),
    path('search' , views.Globe_searching , name="search"),

]   