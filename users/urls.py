from django.urls import include, path

from .views import  *

urlpatterns = [
    path("sign-up/", UserSignUpAPIView.as_view()),
    path("login/", UserLoginAPIView.as_view(), name="login"),
]
