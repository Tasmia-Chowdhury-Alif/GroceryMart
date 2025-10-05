from django.contrib.auth.models import User

from . import models

from djoser.serializers import (
    UserCreateSerializer as BaseUserCreateSerializer,
    UserSerializer as BaseUserSerializer,
)

from rest_framework import serializers


class UserCreateSerializer(BaseUserCreateSerializer):
    """Serializer for creating a new user with Djoser integration."""

    # Explicitly define re_password as a write-only field
    re_password = serializers.CharField(write_only=True)

    class Meta(BaseUserCreateSerializer.Meta):
        model = User
        fields = BaseUserCreateSerializer.Meta.fields + ("first_name", "last_name")

    def validate(self, data):
        # Call parent validation first
        data = super().validate(data)

        # Add custom validation if needed
        # if data["password"] != data["re_password"]:
        #     raise serializers.ValidationError("Passwords do not match.")

        return data

    def create(self, validated_data):
        user = super().create(validated_data)
        return user


class UserSerializer(BaseUserSerializer):
    """Serializer for user details."""
    class Meta(BaseUserSerializer.Meta):
        model = User
        fields = ["id", "username", "first_name", "last_name", "email"]


class ProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile details."""
    class Meta:
        model = models.Profile
        fields = ["user", "full_name", "phone", "address", "image", "shopping_prefs"]
