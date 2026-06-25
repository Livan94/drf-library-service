from drf_spectacular.utils import extend_schema
from rest_framework import generics, permissions
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
    TokenRefreshSerializer,
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from users.serializers import UserMeSerializer, UserRegisterSerializer


class RegisterView(generics.CreateAPIView):
    serializer_class = UserRegisterSerializer
    permission_classes = (permissions.AllowAny,)

    @extend_schema(
        tags=["Users"],
        summary="Register user",
        description="Register a new user account and create "
        "a profile for library service access.",
        request=UserRegisterSerializer,
        responses={201: UserRegisterSerializer},
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = UserMeSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user

    @extend_schema(
        tags=["Users"],
        summary="Get my profile",
        description="Retrieve the profile data of the currently authenticated user.",
        responses={200: UserMeSerializer},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        tags=["Users"],
        summary="Update my profile",
        description="Fully update the profile of the currently authenticated user.",
        request=UserMeSerializer,
        responses={200: UserMeSerializer},
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(
        tags=["Users"],
        summary="Partially update my profile",
        description="Partially update selected profile fields "
        "of the currently authenticated user.",
        request=UserMeSerializer,
        responses={200: UserMeSerializer},
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


class UserTokenObtainPairView(TokenObtainPairView):
    @extend_schema(
        tags=["Users"],
        summary="Obtain JWT token pair",
        description="Authenticate user by email and password "
        "and obtain access and refresh tokens.",
        request=TokenObtainPairSerializer,
        responses={200: TokenObtainPairSerializer},
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class UserTokenRefreshView(TokenRefreshView):
    @extend_schema(
        tags=["Users"],
        summary="Refresh access token",
        description="Obtain a new access token using a valid refresh token.",
        request=TokenRefreshSerializer,
        responses={200: TokenRefreshSerializer},
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
