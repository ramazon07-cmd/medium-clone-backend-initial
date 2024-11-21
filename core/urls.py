from django.urls import path, include
from django.http import JsonResponse
from django.contrib import admin
from django.conf import settings
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from django.conf.urls.static import static
from django.contrib.auth.decorators import user_passes_test

def is_superuser(user):
    return user.is_authenticated

urlpatterns = [
    path("admin/", admin.site.urls),
    path('health/', lambda _: JsonResponse({'detail': 'Healthy'}), name='health'),
    path('users/', include('users.urls')),
    path('', include('articles.urls')),
    path('', lambda _: JsonResponse({'detail': 'Healthy'}), name='health'),
    path('schema/', user_passes_test(is_superuser)(SpectacularAPIView.as_view()), name='schema'),
    path('swagger/', user_passes_test(is_superuser)(SpectacularSwaggerView.as_view()), name='swagger-ui'),
    path('redoc/', user_passes_test(is_superuser)(SpectacularRedocView.as_view()), name='redoc'),
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
