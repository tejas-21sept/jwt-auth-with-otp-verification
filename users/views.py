# from django.contrib.auth import authenticate
# from rest_framework import status
# from rest_framework.response import Response
# from rest_framework.views import APIView
# from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

# from .serializers import  UserSignUpSerializer
# from .utils import api_response, get_status_message

# # class UserLoginAPIView(APIView):
# #     def post(self, request):
# #         try:
# #             serializer = UserLoginSerializer(data=request.data)
# #             print("\nLogin Serializer\n")
# #             if serializer.is_valid():
# #                 print("Valid serializer")
# #                 return self._extracted_from_post_(serializer)
# #             return Response(
# #                 api_response(status_code=400, data=serializer.errors),
# #                 status=status.HTTP_400_BAD_REQUEST,
# #             )
# #         except Exception as e:
# #             return Response(
# #                 api_response(status_code=500, data=str(e)),
# #                 status=status.HTTP_500_INTERNAL_SERVER_ERROR,
# #             )

# #     def _extracted_from_post_(self, serializer):
# #         validated_data = serializer.validated_data
# #         if not isinstance(validated_data, dict):
# #             return Response(
# #                 api_response(
# #                     status_code=400,
# #                     data={"error": "Invalid data format."},
# #                 ),
# #                 status=status.HTTP_400_BAD_REQUEST,
# #             )
# #         user = validated_data.get("user")
# #         if user is None:
# #             # User authentication failed
# #             return Response(
# #                 api_response(
# #                     status_code=400,
# #                     data={"error": "Invalid username or password."},
# #                 ),
# #                 status=status.HTTP_400_BAD_REQUEST,
# #             )
# #         access = AccessToken.for_user(user)
# #         print("Access token:", access)
# #         return (
# #             Response(
# #                 api_response(
# #                     status_code=200,
# #                     data={
# #                         "access": str(access),
# #                         "expires_in": access.payload.get("exp"),
# #                     },
# #                 ),
# #                 status=status.HTTP_200_OK,
# #             )
# #             if access
# #             else Response(
# #                 api_response(
# #                     status_code=400,
# #                     data={"error": "Failed to generate access token."},
# #                 ),
# #                 status=status.HTTP_400_BAD_REQUEST,
# #             )
# #         )


# class UserLoginAPIView(APIView):
#     def post(self, request):
#         serializer = LoginSerializer(data=request.data)
#         if serializer.is_valid():
#             username = serializer.data.get("username")
#             password = serializer.data.get("password")
#             user = authenticate(request=request, username=username, password=password)
#             if user:
#                 tokens = LoginSerializer.get_tokens_for_user(user)
#                 return Response(tokens, status=status.HTTP_200_OK)
#             else:
#                 return Response(
#                     {"error": "Invalid username or password."},
#                     status=status.HTTP_400_BAD_REQUEST,
#                 )
#         else:
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class UserSignUpAPIView(APIView):
#     def post(self, request):
#         serializer = UserSignUpSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken
from .models import CustomUser
from .serializers import LoginSerializer, UserSignUpSerializer, VerifyOTPSerializer
from .utils import api_response, get_status_message

class UserLoginAPIView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.data.get("username")
            password = serializer.data.get("password")
            user = authenticate(request=request, username=username, password=password)
            if user:
                if user.is_verified:
                    access = AccessToken.for_user(user)
                    return Response(
                        {"access": str(access), "expires_in": access.payload.get("exp")},
                        status=status.HTTP_200_OK,
                    )
                else:
                    # If the user is not verified, send OTP for verification
                    user.send_otp()  # Send OTP to user's email
                    return Response(
                        {"detail": "Email verification required. OTP sent to your email."},
                        status=status.HTTP_401_UNAUTHORIZED,
                    )
            else:
                return Response(
                    {"error": "Invalid username or password."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserSignUpAPIView(APIView):
    def post(self, request):
        serializer = UserSignUpSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.send_otp()  # Send OTP to user's email for verification
            return Response(
                {"detail": "Account created. OTP sent to your email for verification."},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.data.get("email")
            otp = serializer.data.get("otp")
            try:
                user = CustomUser.objects.get(email=email)
                if user.verify_otp(otp):
                    access = AccessToken.for_user(user)
                    return Response(
                        {"access": str(access), "expires_in": access.payload.get("exp")},
                        status=status.HTTP_200_OK,
                    )
                else:
                    return Response(
                        {"error": "Invalid OTP."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            except CustomUser.DoesNotExist:
                return Response(
                    {"error": "User with this email does not exist."},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
