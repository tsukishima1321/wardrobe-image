from typing import List
from django.urls import URLPattern, path
from . import views

app_name: str = 'wardrobe_image'

urlpatterns: List[URLPattern] = [
    path('auth/', views.auth_request, name='auth_request'),
    path('token/', views.MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', views.TokenRefreshView.as_view(), name='token_refresh'),
    path('thumbnails/medium/<str:imageName>', views.generate_medium_thumbnail, name='generate_medium_thumbnail'),
    path('thumbnails/small/<str:imageName>', views.generate_small_thumbnail, name='generate_small_thumbnail'),
    path('thumbnails/<str:imageName>', views.genarate_thumbnail, name='genarate_thumbnail'),
    path('upload/', views.upload_image, name='upload_image'),
    path('deletefile/', views.delete_image, name='delete_image'),
]
