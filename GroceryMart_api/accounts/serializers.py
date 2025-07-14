from django.contrib.auth.models import User

from . import models 

from djoser.serializers import (
    UserCreateSerializer as BaseUserCreateSerializer,
    UserSerializer as BaseUserSerializer,
)

from rest_framework import serializers


class UserCreateSerializer(BaseUserCreateSerializer):
    # Explicitly define re_password as a write-only field
    re_password = serializers.CharField(write_only=True)
    
    class Meta(BaseUserCreateSerializer.Meta):
        model = User
        fields = BaseUserCreateSerializer.Meta.fields + ('first_name', 'last_name')

    def validate(self, data):
        # Call parent validation first
        data = super().validate(data)

        # Add custom validation if needed
        # if data["password"] != data["re_password"]:
        #     raise serializers.ValidationError("Passwords do not match.")

        return data

    def create(self, validated_data):
        # Debug: Print what we're receiving
        print("DEBUG - validated_data:", validated_data)
        
        # Let the parent class handle the creation
        # This ensures Djoser's logic is preserved
        user = super().create(validated_data)
        
        # Debug: Print created user
        print("DEBUG - Created user:", user.username, user.first_name, user.last_name)
        
        return user


class UserSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        model = User
        fields = ["id", "username", "first_name", "last_name", "email"]


# class RegistrationSerializer(serializers.ModelSerializer):
#     confirm_password = serializers.CharField(required=True)

#     class Meta:
#         model = User
#         fields = [
#             "username",
#             "first_name",
#             "last_name",
#             "email",
#             "password",
#             "confirm_password",
#         ]
#         extra_kwargs = {
#             "password": {"write_only": True},
#             "confirm_password": {"write_only": True},
#         }

#     def validate(self, data):
#         email = data.get("email", "").lower()
#         data["email"] = email  # Normalizeing the email

#         if data["password"] != data["confirm_password"]:
#             raise serializers.ValidationError("Passwords do not match.")

#         # if User.objects.filter(email=email).exists():
#         #     raise serializers.ValidationError("Email already exists.")

#         return data

#     def create(self, validated_data):
#         user = User(
#             username=validated_data["username"],
#             first_name=validated_data["first_name"],
#             last_name=validated_data["last_name"],
#             email=self.validated_data["email"],
#             is_active=False,
#         )

#         user.set_password(validated_data["password"])
#         user.save()
#         return user



class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Profile
        fields = ['user', 'full_name', 'phone', 'address', 'image', 'shopping_prefs']