from django.contrib.auth.models import User

from djoser.serializers import (
    UserCreateSerializer as BaseUserCreateSerializer,
    UserSerializer as BaseUserSerializer,
)

from rest_framework import serializers


class UserCreateSerializer(BaseUserCreateSerializer):
    confirm_password = serializers.CharField(required=True)

    class Meta(BaseUserCreateSerializer.Meta):
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "password",
            "re_password",
        ]
        extra_kwargs = {
            "password": {"write_only": True},
            "re_password": {"write_only": True},
        }

    def validate(self, data):
        # email = data.get("email", "").lower()
        # data["email"] = email  # Normalizeing the email

        if data["password"] != data["re_password"]:
            raise serializers.ValidationError("Passwords do not match.")

        # if User.objects.filter(email=email).exists():
        #     raise serializers.ValidationError("Email already exists.")

        return data

    def create(self, validated_data):
        validated_data.pop("re_password")
        print("Creating user with:", validated_data)
        user = User.objects.create_user(**validated_data)
        print("Saved user first_name:", user.first_name)
        print("Saved user last_name:", user.last_name)
        
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
