from django.contrib.auth import authenticate
from django.contrib.auth.models import User

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, generics, viewsets

from rest_framework_simplejwt.tokens import RefreshToken

from .models import PersonalDetails, BodyDetails
from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    PersonalDetailsSerializer,
    BodyDetailsSerializer,
)


# -------------------------
# AUTH
# -------------------------
class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(
            {"message": "Registered successfully", "email": user.email},
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        # because username=email during register
        user = authenticate(username=email, password=password)
        if user is None:
            return Response({"detail": "Invalid email or password"}, status=status.HTTP_400_BAD_REQUEST)

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "message": "Login successful",
                "user": {"id": user.id, "email": user.email},
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            status=status.HTTP_200_OK,
        )


# -------------------------
# PERSONAL DETAILS (ONE per USER)
# -------------------------
class PersonalDetailsCreateView(generics.CreateAPIView):
    serializer_class = PersonalDetailsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        # allow only one record
        if PersonalDetails.objects.filter(user=request.user).exists():
            return Response(
                {"detail": "Personal details already exist. Use PUT /api/personal/ to update."},
                status=400,
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class PersonalDetailsView(generics.RetrieveUpdateAPIView):
    serializer_class = PersonalDetailsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        obj, _ = PersonalDetails.objects.get_or_create(
            user=self.request.user,
            defaults={"full_name": "", "age": 0, "gender": "male"},
        )
        return obj


# -------------------------
# BODY DETAILS (MANY per USER)
# -------------------------
class BodyDetailsViewSet(viewsets.ModelViewSet):
    serializer_class = BodyDetailsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return BodyDetails.objects.filter(user=self.request.user).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)