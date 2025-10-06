from django.shortcuts import render
from django.contrib.auth.models import User

from rest_framework import generics, status, viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, BasePermission

from . import models, serializers

from drf_spectacular.utils import extend_schema_view, extend_schema


class IsOwner(BasePermission):
    """Permission to allow only owners to edit their profile."""
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user

@extend_schema_view(
    list=extend_schema(summary="List all user profiles", tags=['Accounts']),
    retrieve=extend_schema(summary="Retrieve a user profile", tags=['Accounts']),
    create=extend_schema(summary="Create a user profile", tags=['Accounts']),
    update=extend_schema(summary="Update a user profile", tags=['Accounts']),
    partial_update=extend_schema(summary="Partially update a user profile", tags=['Accounts']),
    destroy=extend_schema(summary="Delete a user profile", tags=['Accounts']),
)
class ProfileViewset(viewsets.ModelViewSet):
    queryset = models.Profile.objects.all()
    serializer_class = serializers.ProfileSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    # Limit queryset to user's own profile for non-admin
    def get_queryset(self):
        if self.request.user.is_staff:
            return super().get_queryset()
        return models.Profile.objects.filter(user=self.request.user)
