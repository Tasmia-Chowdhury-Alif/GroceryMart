from django.contrib.auth.models import User

from rest_framework import serializers


class RegistrationSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "password",
            "confirm_password",
        ]
        extra_kwargs = {
            "password": {"write_only": True},
            "confirm_password": {"write_only": True},
        }

    def validate(self, data):
        email = data.get("email", "").lower()
        data["email"] = email  # Normalizeing the email

        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError("Passwords do not match.")

        # if User.objects.filter(email=email).exists():
        #     raise serializers.ValidationError("Email already exists.")

        return data

    def create(self, validated_data):
        user = User(
            username=validated_data["username"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            email=self.validated_data["email"],
            is_active=False,
        )

        user.set_password(validated_data["password"])
        user.save()
        return user

    def save(self):
        username = self.validated_data["username"]
        first_name = self.validated_data["first_name"]
        last_name = self.validated_data["last_name"]
        email = self.validated_data["email"]
        password1 = self.validated_data["password"]
        confirm_password = self.validated_data["confirm_password"]

        if password1 != confirm_password:
            raise serializers.ValidationError({"error": "Password Doesn't match"})
        elif User.objects.filter(email=email).exists():
            raise serializers.ValidationError({"error": "Email Already exists"})

        user = User(
            username=username, first_name=first_name, last_name=last_name, email=email
        )
        print(user)
        user.set_password(password1)
        user.is_active = False
        user.save()
        return user
