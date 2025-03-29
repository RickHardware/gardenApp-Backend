from django.urls import path
from . import views
from django.contrib.auth import views as django_views
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('', views.user_list, name='user-list'),
    
    ##Garden Specific URLs
    path('gardenlist/<str:username>/',views.user_garden_list,name='garden-user-list'),
    path('garden/',views.garden_list,name='garden-list'),
    path('postGarden/', views.create_garden, name='garden-post'),
    path('gardensearch/',views.garden_search,name='garden-search'),
    path('message/<str:gardenName>' , views.message_list, name = 'message-list'),
    
        ##Message specific URLs
    path('msg/get/<str:gardenID>/', views.message_get, name='message-get'),
    path('msg/', views.create_message, name='message-post'),

    ##User specific URLs
    path('user/<str:id>/', views.user_get, name='user-specific'),
    path('post/', views.create_user, name='user-post'),


    #Follower specific URLS:
    path('garden/join/<str:gardenName>/', views.create_garden_follower, name='follower-post'),
    path('garden/leave/<str:gardenName>/', views.remove_garden_follower, name='unfollower-post'),
    path('garden/followers/<str:gardenID>/', views.get_follower_list, name='followed-get'),
    path('user/followed/<str:userID>/', views.get_followed_gardens, name='follower-get'),
    

    
    #Plant info and LLM URLs
    path('plants/', views.proxy_plants, name='proxy_plants'),
    path("chat/", views.chat_view),

    #Authentication and log in URLS
    path('logout/', views.logoutUser, name = 'logout-user'),
    path('login/', views.loginUser, name = 'login-user'),
    path('loginStatus/', views.checkUserStatus, name = 'login-status'),
    path('password-reset/', views.resetPasswordEmail, name='password_reset'),   
    #django prebuilt
    path('reset/<uidb64>/<token>/', django_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', django_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]



