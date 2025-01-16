from django.http import HttpResponse
from django.http import HttpResponseNotFound
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from PIL import Image
import os
import hashlib

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def auth_request(request):
    return HttpResponse(status=status.HTTP_200_OK)

from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView

class MyTokenObtainPairView(TokenObtainPairView):
    pass

class TokenRefreshView(TokenRefreshView):
    pass

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_image(request):
    if request.method == 'POST':
        image = request.FILES.get('image')
        if image is None:
            return HttpResponse('No image provided', status=400)
        # Generate a unique name for the image by md5
        image.name = hashlib.md5(image.read()).hexdigest() + "." + image.name.split('.')[-1]
        imagePath = os.path.join(settings.IMAGE_STORAGE_PATH + image.name)
        with open(imagePath, 'wb') as f:
            for chunk in image.chunks():
                f.write(chunk)
        return HttpResponse('Image uploaded', status=201)
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