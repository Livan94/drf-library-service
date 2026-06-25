from django.urls import path

from users.views import (
    MeView,
    RegisterView,
    UserTokenObtainPairView,
    UserTokenRefreshView,
)

urlpatterns = [
    path("", RegisterView.as_view(), name="register"),
    path("token/", UserTokenObtainPairView.as_view(), name="token-obtain"),
    path("token/refresh/", UserTokenRefreshView.as_view(), name="token-refresh"),
    path("me/", MeView.as_view(), name="me"),
]
