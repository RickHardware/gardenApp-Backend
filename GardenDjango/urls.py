from django.contrib import admin
from django.urls import path, include
from gardenapp import views  
from djoser import urls
urlpatterns = [
    path('api/', include('gardenapp.urls')),  
    path('admin/', admin.site.urls),         
    path('', views.index, name='home'),      
    path(r'^auth/', include('djoser.urls')),
]
