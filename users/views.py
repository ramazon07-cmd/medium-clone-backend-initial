from rest_framework import status, permissions, generics, parsers, exceptions, views
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from django.contrib.auth import authenticate, update_session_auth_hash
from rest_framework.exceptions import ValidationError
from django_redis import get_redis_connection
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from articles.models import Article
from django.http import JsonResponse
from .serializers import (
    UserSerializer,
    RecommendationSerializer,
    LoginSerializer,
    ValidationErrorSerializer,
    TokenResponseSerializer,
    UserUpdateSerializer,
    FollowerSerializer,
    ChangePasswordSerializer,
    ForgotPasswordRequestSerializer,
    ForgotPasswordVerifyRequestSerializer,
    ResetPasswordResponseSerializer,
    ForgotPasswordVerifyResponseSerializer,
    ForgotPasswordResponseSerializer,
)
from drf_spectacular.utils import extend_schema, extend_schema_view
from .services import UserService, SendEmailService, OTPService
from django.contrib.auth.hashers import make_password
from secrets import token_urlsafe
from .errors import ACTIVE_USER_NOT_FOUND_ERROR_MSG
from .models import Recommendation, Follow, CustomUser

User = get_user_model()

@extend_schema_view( # database ma'lumotlari
    post=extend_schema(
        summary="Sign up a new user",
        request=UserSerializer,
        responses={
            201: UserSerializer,
            400: ValidationErrorSerializer
        }
    )
)

class SignupView(APIView):
    serializer_class = UserSerializer
    permission_classes = (permissions.AllowAny,) # serializerdan foydalanish sharti

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            user_data = UserSerializer(user).data
            return Response({
                'user': user_data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@extend_schema_view(
    post=extend_schema(
        summary="Log in a user",
        request=LoginSerializer,
        responses={
            200: TokenResponseSerializer,
            400: ValidationErrorSerializer,
        }
    )
)

class LoginView(APIView):
    serializer_class = LoginSerializer
    permission_classes = [permissions.AllowAny] # serializerdan foydalanish sharti

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(
            request,
            username=serializer.validated_data['username'],
            password=serializer.validated_data['password']
        )

        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'Hisob maʼlumotlari yaroqsiz'}, status=status.HTTP_401_UNAUTHORIZED)



@extend_schema_view(
    get=extend_schema(
        summary="Get user information",
        responses={
            200: UserSerializer,
            400: ValidationErrorSerializer
        }
    ),
    patch=extend_schema(
        summary="Update user information",
        request=UserUpdateSerializer,
        responses={
            200: UserUpdateSerializer,
            400: ValidationErrorSerializer
        }
    )
)
class UsersMe(generics.RetrieveAPIView, generics.UpdateAPIView):
    http_method_names = ['get', 'patch']
    queryset = User.objects.filter(is_active=True)
    parser_classes = [parsers.MultiPartParser]
    permission_classes = (IsAuthenticated,) # serializerdan foydalanish sharti

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method == 'PATCH':
            return UserUpdateSerializer
        return UserSerializer

    def patch(self, request, *args, **kwargs):
        redis_conn = get_redis_connection('default')
        redis_conn.set('test_key', 'test_value', ex=3600)
        cached_value = redis_conn.get('test_key')
        print(cached_value)

        return super().partial_update(request, *args, **kwargs)

@extend_schema_view(
    post=extend_schema(
        summary="Log out a user",
        request=None,
        responses={
            200: ValidationErrorSerializer,
            401: ValidationErrorSerializer
        }
    )
)
class LogoutView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated] # serializerdan foydalanish sharti

    @extend_schema(responses=None)
    def post(self, request, *args, **kwargs):
        UserService.create_tokens(request.user, access='fake_token', refresh='fake_token', is_force_add_to_redis=True)
        return Response({"detail": "Mufaqqiyatli chiqildi."})

@extend_schema_view(
    put=extend_schema(
        summary="Change user password",
        request=ChangePasswordSerializer,
        responses={
            200: TokenResponseSerializer,
            401: ValidationErrorSerializer
        }
    )
)
class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated] # serializerdan foydalanish sharti
    serializer_class = ChangePasswordSerializer

    def put(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(
            request,
            username=request.user.username,
            password=serializer.validated_data['old_password']
        )

        if user is not None:
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            update_session_auth_hash(request, user)
            tokens = UserService.create_tokens(user, is_force_add_to_redis=True)
            return Response(tokens)
        else:
            raise ValidationError("Eski parol xato.")

@extend_schema_view(
    post=extend_schema(
        summary="Forgot Password",
        request=ForgotPasswordRequestSerializer,
        responses={
            200: ForgotPasswordResponseSerializer,
            401: ValidationErrorSerializer
        }
    )
)
class ForgotPasswordView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny] # serializerdan foydalanish sharti
    serializer_class = ForgotPasswordRequestSerializer
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        users = User.objects.filter(email=email, is_active=True)
        if not users.exists():
            raise exceptions.NotFound(ACTIVE_USER_NOT_FOUND_ERROR_MSG)

        otp_code, otp_secret = OTPService.generate_otp(email=email, expire_in=2 * 60)

        try:
            SendEmailService.send_email(email, otp_code)
            return Response({
                "email": email,
                "otp_secret": otp_secret,
            })
        except Exception:
            redis_conn = OTPService.get_redis_conn()
            redis_conn.delete(f"{email}:otp")
            raise ValidationError("Emailga xabar yuborishda xatolik yuz berdi")

@extend_schema_view(
    post=extend_schema(
        summary="Forgot Password Verify",
        request=ForgotPasswordVerifyRequestSerializer,
        responses={
            200: ForgotPasswordVerifyResponseSerializer,
            401: ValidationErrorSerializer
        }
    )
)
class ForgotPasswordVerifyView(generics.CreateAPIView):
    permission_classes = [permissions.AllowAny] # serializerdan foydalanish sharti
    serializer_class = ForgotPasswordVerifyRequestSerializer
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        redis_conn = OTPService.get_redis_conn()
        otp_secret = kwargs.get('otp_secret')
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        otp_code = serializer.validated_data['otp_code']
        email = serializer.validated_data['email']
        users = User.objects.filter(email=email, is_active=True)
        if not users.exists():
            raise exceptions.NotFound(ACTIVE_USER_NOT_FOUND_ERROR_MSG)
        OTPService.check_otp(email, otp_code, otp_secret)
        redis_conn.delete(f"{email}:otp")
        token_hash = make_password(token_urlsafe())
        redis_conn.set(token_hash, email, ex=2 * 60 * 60)
        return Response({"token": token_hash})

@extend_schema_view(
    patch=extend_schema(
        summary="Reset Password",
        request=ResetPasswordResponseSerializer,
        responses={
            200: TokenResponseSerializer,
            401: ValidationErrorSerializer
        }
    )
)
class ResetPasswordView(generics.UpdateAPIView):
    serializer_class = ResetPasswordResponseSerializer
    permission_classes = [permissions.AllowAny] # serializerdan foydalanish sharti
    http_method_names = ['patch']
    authentication_classes = []

    def patch(self, request, *args, **kwargs):
        redis_conn = OTPService.get_redis_conn()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token_hash = serializer.validated_data['token']
        email = redis_conn.get(token_hash)

        if not email:
            raise ValidationError("Token yaroqsiz")

        users = User.objects.filter(email=email.decode(), is_active=True)
        if not users.exists():
            raise exceptions.NotFound(ACTIVE_USER_NOT_FOUND_ERROR_MSG)

        password = serializer.validated_data['password']
        user = users.first()
        user.set_password(password)
        user.save()

        update_session_auth_hash(request, user)
        tokens = UserService.create_tokens(user, is_force_add_to_redis=True)
        redis_conn.delete(token_hash)
        return Response(tokens)

class RecommendationView(APIView):
    serializer_class = RecommendationSerializer
    permission_classes = (permissions.IsAuthenticated,) # serializerdan foydalanish sharti

    def post(self, request):
        more_article_id = request.data.get('more_article_id') # ma'lumotlarni olish
        less_article_id = request.data.get('less_article_id') # ma'lumotlarni olish
        user = request.user
        recommendation, _ = Recommendation.objects.get_or_create(user=user)

        if more_article_id:
            article = Article.objects.get(id=more_article_id)
            if article in recommendation.less_recommend.all():
                recommendation.less_recommend.remove(article)
            recommendation.more_recommend.add(article)

        elif less_article_id:
            article = Article.objects.get(id=less_article_id)
            if article in recommendation.more_recommend.all():
                recommendation.more_recommend.remove(article)
            recommendation.less_recommend.add(article)

        return Response(status=status.HTTP_204_NO_CONTENT)

class PopularAuthorsView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, id):
        # Get the user to unfollow
        user_to_unfollow = get_object_or_404(User, id=id)

        # Check if the current user is following the other user
        if not request.user.is_following(user_to_unfollow):
            return Response({"detail": "You are not following this user."}, status=status.HTTP_404_NOT_FOUND)

        # Perform the unfollow action
        request.user.unfollow(user_to_unfollow)

        # Return a success response
        return Response({"detail": "Successfully unfollowed."}, status=status.HTTP_204_NO_CONTENT)


class AuthorFollowView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, author_id):
        user = request.user
        try:
            author = User.objects.get(id=author_id)
            if user == author:
                return Response({"detail": "You cannot follow yourself."}, status=status.HTTP_400_BAD_REQUEST)

            user.following.add(author)  # Add the author to the user's following set
            user.save()

            return Response({"detail": "Muvaffaqiyatli follow qilindi."}, status=status.HTTP_201_CREATED)
        except User.DoesNotExist:
            return Response({"detail": "Author not found."}, status=status.HTTP_404_NOT_FOUND)


    def delete(self, request, author_id):
        """
        Unfollow an author.
        """
        try:
            author = User.objects.get(id=author_id)
        except User.DoesNotExist:
            return Response({"detail": "Author not found."}, status=status.HTTP_404_NOT_FOUND)

        if author == request.user:
            return Response({"detail": "You cannot unfollow yourself."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the user is following the author
        try:
            follow = Follow.objects.get(follower=request.user, followee=author)
            follow.delete()
            return Response({"detail": "Successfully unfollowed the author."}, status=status.HTTP_204_NO_CONTENT)
        except Follow.DoesNotExist:
            return Response({"detail": "You are not following this author."}, status=status.HTTP_404_NOT_FOUND)

class FollowersListView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.followers_set.all()

class FollowingListView(APIView):
    def get(self, request):
        user = request.user
        following = user.following.all()
        serializer = UserSerializer(following, many=True)
        return Response({"results": serializer.data})

class FollowerListView(ListAPIView):
    serializer_class = FollowerSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Follow.objects.filter(followee=self.request.user)

class UnfollowAuthorView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, id):
        try:
            user_to_unfollow = User.objects.get(id=id)
            request.user.unfollow(user_to_unfollow)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except User.DoesNotExist:
            return Response({"detail": "Foydalanuvchi topilmadi."}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
