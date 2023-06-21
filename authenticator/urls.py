from django.urls import path

from .views import RegisterView, LoginView, LogoutView, IndexView, UserActivationView

app_name = "authenticator"

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("activate/<uidb64>/<token>", UserActivationView.as_view(), name="activate")
]
