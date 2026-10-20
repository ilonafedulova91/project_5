from drf_spectacular.utils import extend_schema
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import TelegramProfile
from .serializers import RegisterSerializer, TelegramProfileSerializer


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class TelegramProfileView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=TelegramProfileSerializer,
        responses={200: TelegramProfileSerializer},
    )
    def post(self, request):
        serializer = TelegramProfileSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)

        profile, _ = TelegramProfile.objects.update_or_create(
            user=request.user,
            defaults={"chat_id": serializer.validated_data["chat_id"]},
        )

        return Response(
            TelegramProfileSerializer(profile).data,
            status=200,
        )
