from django.contrib import admin
from django.urls import path, include
from contratista_test import settings
from django.conf.urls.static import static

urlpatterns = [
    path('contratista_testing_admin/', admin.site.urls),
    path('contratista_test_api/', include('contratista_test_app.urls')),
    path('o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('schema/', include('django_spaghetti.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)