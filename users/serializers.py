from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import TelegramProfile

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        validators=[validate_password],
    )

    class Meta:
        model = User
        fields = ("id", "username", "email", "password")

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class TelegramProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelegramProfile
        fields = ("chat_id",)
        extra_kwargs = {
            "chat_id": {"required": True, "allow_null": False},
        }

    def validate_chat_id(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "Telegram chat_id должен быть положительным числом."
            )

        if (
            TelegramProfile.objects.filter(chat_id=value)
            .exclude(user=self.context["request"].user)
            .exists()
        ):
            raise serializers.ValidationError(
                "Этот Telegram chat_id уже привязан к другому пользователю."
            )

        return value
