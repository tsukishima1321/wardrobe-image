"""
URL configuration for wardrobe project.

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

app_name = 'wardrobe_image'

urlpatterns = [
    path('auth/', views.auth_request, name='auth_request'),
    path('token/', views.MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', views.TokenRefreshView.as_view(), name='token_refresh'),
    path('thumbnails/<str:imageName>', views.genarate_thumbnail, name='genarate_thumbnail'),
    path('upload/', views.upload_image, name='upload_image'),
]
