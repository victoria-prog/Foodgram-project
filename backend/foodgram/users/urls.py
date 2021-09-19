from django.urls import include, path
from rest_framework.routers import SimpleRouter

from . import views

app_name = 'users'


router = SimpleRouter()
router.register(r'users', views.UserCustomViewSet, basename='users')
urlpatterns = [
    path('auth/token/login/', views.get_token),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls)),
]
