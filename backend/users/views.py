from typing import List

from rest_framework import generics, mixins, status
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer

from .models import User
from .serializers import UserNewPasswordSerializer, UserSerializer, UserUpdateSerializer


class UserAPIView(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.CreateModelMixin,
    generics.GenericAPIView,
):
    def get(self, request: Request, *args, **kwargs) -> Response:
        return self.retrieve(request, *args, **kwargs)

    def post(self, request: Request, *args, **kwargs) -> Response:
        return self.create(request, *args, **kwargs)

    def put(self, request: Request, *args, **kwargs) -> Response:
        return self.update(request, *args, **kwargs)

    def patch(self, request: Request, *args, **kwargs) -> Response:
        if "new_password" in request.data and "current_password" not in request.data:
            return Response(
                {
                    "message": "You must provide current password to set new one",
                    "code": "current_password_required",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        elif "new_password" in request.data and "current_password" in request.data:
            user = User.objects.get(id=request.user.id)
            if not user.check_password(request.data.get("current_password")):
                return Response(
                    {
                        "message": "Provided password is incorrect",
                        "code": "incorrect_password",
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )
        return self.partial_update(request, *args, **kwargs)

    def get_serializer_class(self) -> ModelSerializer:
        if self.request.method == "PATCH" and "new_password" in self.request.data:
            return UserNewPasswordSerializer
        elif self.request.method in ["PUT", "PATCH"]:
            return UserUpdateSerializer
        return UserSerializer

    def get_permissions(self) -> List[BasePermission]:
        if self.request.method == "POST":
            return []
        return [IsAuthenticated()]

    def get_object(self):
        return self.request.user
