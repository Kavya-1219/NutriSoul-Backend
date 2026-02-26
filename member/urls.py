from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import RegisterView, LoginView, PersonalDetailsView, PersonalDetailsCreateView, BodyDetailsViewSet

router = DefaultRouter()
router.register(r"body", BodyDetailsViewSet, basename="body")

urlpatterns = [
    # AUTH
    path("auth/register/", RegisterView.as_view()),
    path("auth/login/", LoginView.as_view()),          # ✅ email + password
    path("auth/refresh/", TokenRefreshView.as_view()), # refresh token

    # PERSONAL DETAILS
    path("personal/create/", PersonalDetailsCreateView.as_view()),
    path("personal/", PersonalDetailsView.as_view()),

    # BODY DETAILS
    path("", include(router.urls)),
]