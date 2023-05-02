from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from cosmetica.views import *
from cosmeticaSite import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('captcha/', include('captcha.urls')),
    path('api/v1/users/', UserViewSet.as_view({'get': 'list', 'post': 'create', })),
    path('api/v1/users/<int:pk>/', UserViewSet.as_view({'get': 'retrieve', 'delete': 'destroy', 'put': "update", })),
    path('api/v1/products/', ItemViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('api/v1/products/<int:pk>/', ItemViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'})),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # path('api/auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('', include('cosmetica.urls')),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [path('__debug__/', include(debug_toolbar.urls)), ] + urlpatterns
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = pageNotFound
handler403 = error403
handler400 = error400
handler500 = server_error
