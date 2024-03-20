# from django.contrib.auth import authenticate
# from rest_framework import serializers
# from rest_framework_simplejwt.tokens import RefreshToken, Token

# from .models import CustomUser


# class UserSignUpSerializer(serializers.ModelSerializer):
#     password = serializers.CharField(write_only=True)

#     class Meta:
#         model = CustomUser
#         fields = [
#             "username",
#             "email",
#             "password",
#             "first_name",
#             "last_name",
#             "mobile_number",
#         ]
#         extra_kwargs = {"password": {"write_only": True}}

#     def create(self, validated_data):
#         return CustomUser.objects.create_user(**validated_data)


# # class UserLoginSerializer(serializers.Serializer):
# #     username = serializers.CharField()
# #     password = serializers.CharField(write_only=True)


# # from django.contrib.auth import authenticate
# # from rest_framework import serializers
# # from rest_framework_simplejwt.tokens import RefreshToken

# # from .models import CustomUser


# class LoginSerializer(serializers.Serializer):
#     username = serializers.CharField(max_length=150)
#     password = serializers.CharField(
#         label="Password",
#         style={"input_type": "password"},
#         trim_whitespace=False,
#     )

#     def validate(self, attrs):
#         username = attrs.get("username")
#         password = attrs.get("password")

#         if username and password:
#             user = authenticate(
#                 request=self.context.get("request"),
#                 username=username,
#                 password=password,
#             )

#             if not user:
#                 msg = "Unable to log in with provided credentials."
#                 raise serializers.ValidationError(msg, code="authorization")
#         else:
#             msg = "Must include 'username' and 'password'."
#             raise serializers.ValidationError(msg, code="authorization")

#         attrs["user"] = user  # Set the user in validated_data
#         return attrs

#     def create(self, validated_data):
#         pass

#     def update(self, instance, validated_data):
#         pass

#     @staticmethod
#     def get_tokens_for_user(user):
#         refresh = RefreshToken.for_user(user)
#         access_token = str(refresh)
#         refresh_token = str(refresh)
#         return {
#             "refresh": refresh_token,
#             "access": access_token
#         }

    
from rest_framework import serializers
from .models import CustomUser

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

class UserSignUpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name', 'mobile_number', 'password']

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        return user

class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
