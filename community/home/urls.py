from django.urls import path
from . import views


urlpatterns = [
    path('',views.index,name="index"),
    path('home/',views.home,name="home"),
    path('register/',views.register,name="register"),
    path('login/',views.login,name="login"),
    path('verify/',views.verify,name="verify"),
    path('events/',views.events,name="events"),
    path('profile/',views.profile,name="profile"),
    path('create_event/',views.create_event,name="create_event")
    





]
