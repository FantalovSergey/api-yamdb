from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AdminViewSet, APIToken, APIUser, SignUpViewSet

v1_router = DefaultRouter()
v1_router.register(r'auth/signup', SignUpViewSet, basename='signup')
v1_router.register(r'users', AdminViewSet, basename='user')

urlpatterns = [
    path('v1/auth/token/', APIToken.as_view(), name='get_token'),
    path('v1/users/me/', APIUser.as_view(), name='user_profile'),
    path('v1/', include(v1_router.urls)),
]
