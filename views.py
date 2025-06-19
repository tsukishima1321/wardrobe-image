from django.http import HttpResponse
from django.http import HttpResponseNotFound
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from PIL import Image
import os
import hashlib
from django_ratelimit.decorators import ratelimit
import json

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def auth_request(request):
    return HttpResponse(status=status.HTTP_200_OK)

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

import logging

logger = logging.getLogger('imagebed')

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        # 获取用户IP地址
        request = self.context['request']
        user_ip = request.META.get('REMOTE_ADDR')
        # 将IP地址添加到token中
        refresh = self.get_token(self.user)
        refresh['ip'] = user_ip
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)
        return data
    
class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        refresh = RefreshToken(attrs['refresh'])

        # 获取用户IP地址
        request = self.context['request']
        user_ip = request.META.get('REMOTE_ADDR')

        # 验证IP地址
        if refresh['ip'] != user_ip:
            raise serializers.ValidationError(_('IP address does not match'))

        data = {'access': str(refresh.access_token)}

        if api_settings.ROTATE_REFRESH_TOKENS:
            if api_settings.BLACKLIST_AFTER_ROTATION:
                try:
                    # Attempt to blacklist the given refresh token
                    refresh.blacklist()
                except AttributeError:
                    # If blacklist app not installed, `blacklist` method will
                    # not be present
                    pass

            refresh.set_jti()
            refresh.set_exp()
            data['refresh'] = str(refresh)

        return data

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    pass

class TokenRefreshView(TokenRefreshView):
    serializer_class = CustomTokenRefreshSerializer
    pass

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_image(request):
    if request.method == 'POST':
        image = request.FILES.get('image')
        if image is None:
            return HttpResponse('No image provided', status=400)
        # Generate a unique name for the image by md5
        name = hashlib.md5(image.read()).hexdigest() + "." + image.name.split('.')[-1]
        image.name = name
        imagePath = os.path.join(settings.IMAGE_STORAGE_PATH + image.name)
        if os.path.exists(imagePath):
            return HttpResponse('Image already exists', status=400)
        with open(imagePath, 'wb') as f:
            for chunk in image.chunks():
                f.write(chunk)
        logger.info(f"Image {name} uploaded successfully")
        return HttpResponse(json.dumps({'name': name}), content_type='application/json')
    return HttpResponse('Method not allowed', status=405)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def delete_image(request):
    if request.method == 'POST':
        logger.info(f"Delete image request: {request.data}")
        imageName = request.data.get('imageName')
        if not imageName:
            return HttpResponse('No image name provided', status=400)
        imagePath = os.path.join(settings.IMAGE_STORAGE_PATH + imageName)
        if not os.path.exists(imagePath):
            return HttpResponse('Image not found', status=404)
        try:
            os.remove(imagePath)
            logger.info(f"Image {imageName} deleted successfully")
            thumbnailPath = os.path.join(settings.THUMBNAILS_STORAGE_PATH + imageName)
            if os.path.exists(thumbnailPath):
                os.remove(thumbnailPath)
            return HttpResponse('Image deleted successfully', status=200)
        except Exception as e:
            return HttpResponse(f'Error deleting image: {str(e)}', status=500)
    return HttpResponse('Method not allowed', status=405)
    

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def genarate_thumbnail(request, imageName):
    imagePath = os.path.join(settings.IMAGE_STORAGE_PATH + imageName)
    if not os.path.exists(imagePath):
        return HttpResponseNotFound('Image not found')
    thumbnailPath = os.path.join(settings.THUMBNAILS_STORAGE_PATH + imageName)
    if os.path.exists(thumbnailPath):
        with open(thumbnailPath, 'rb') as f:
            return HttpResponse(f.read(), content_type='image/jpeg')
    try:
        image = Image.open(imagePath)
        if image.mode != 'RGB':
            image = image.convert('RGB')
        if image.width < 400:
            pass
        else:
            w_percent = 400 / float(image.width)
            h_size = int(float(image.height) * w_percent)
            image = image.resize((400, h_size))
        os.makedirs(os.path.dirname(thumbnailPath), exist_ok=True)
        image.save(thumbnailPath, 'JPEG')
        with open(thumbnailPath, 'rb') as f:
            return HttpResponse(f.read(), content_type='image/jpeg')
    except Exception as e:
        return HttpResponse(f'Error processing image: {str(e)}', status=500)
    return HttpResponse(status=status.HTTP_200_OK)