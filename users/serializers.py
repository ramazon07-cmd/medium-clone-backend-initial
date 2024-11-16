from django.contrib.auth import authenticate
from rest_framework import serializers, generics
from django.contrib.auth import get_user_model
from django.conf import settings
from users.errors import BIRTH_YEAR_ERROR_MSG
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from users.models import Recommendation, Follow

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required=True, min_length=1)
    last_name = serializers.CharField(required=True, min_length=1)

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'middle_name', 'email', 'avatar', 'password']
        extra_kwargs = {'password': {'write_only': True}} # parol yozish sharti

    def create(self, validated_data):                # user create qilish uchun method
        user = User(
            email=validated_data.get('email', ''),
            username=validated_data['username'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            middle_name=validated_data.get('middle_name', '')
        )
        user.set_password(validated_data['password']) # user parolini saqlash
        user.avatar = validated_data.get('avatar', '') # user avatarini saqlash
        user.save()  # user ma'lumotlarini saqlash
        return user



class LoginSerializer(serializers.Serializer): # user orqali Login qilish
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):                         # kelgan datani yaroqli ekanligini tekshirish uchun
        username = data.get('username')
        password = data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if user is None:
                raise serializers.ValidationError('Kirish maʼlumotlari notoʻgʻri')
        else:
            raise serializers.ValidationError('Foydalanuvchi nomi va parol ham talab qilinadi')

        data['user'] = user
        return data



class TokenResponseSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    access = serializers.CharField()



class ValidationErrorSerializer(serializers.Serializer):
    detail = serializers.CharField()

    def to_representation(self, instance):
        if isinstance(instance, dict):
            return instance
        return super().to_representation(instance)

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'middle_name', 'email', 'avatar', 'birth_year']

    def validate_birth_year(self, value):
        if not (settings.BIRTH_YEAR_MIN < value < settings.BIRTH_YEAR_MAX):
            raise serializers.ValidationError(BIRTH_YEAR_ERROR_MSG)
        return value

    def validate(self, data):
        birth_year = data.get('birth_year')
        if birth_year is not None:
            if not (settings.BIRTH_YEAR_MIN < birth_year < settings.BIRTH_YEAR_MAX):
                raise serializers.ValidationError({"birth_year": BIRTH_YEAR_ERROR_MSG})
        return data

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_password(self, value):
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(e.messages)
        return value

    def validate(self, data):
        if data['new_password'] == data['old_password']:
            raise serializers.ValidationError("Yangi va eski parollar bir xil bo'lmasligi kerak")
        return data

class ForgotPasswordRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise ValidationError("Email topilmadi.")
        return value

class ForgotPasswordResponseSerializer(serializers.Serializer):
    email = serializers.CharField(required=True)
    otp_secret = serializers.CharField(required=True)

class ForgotPasswordVerifyRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    otp_code = serializers.CharField(required=True, max_length=6)

class ForgotPasswordVerifyResponseSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)

class ResetPasswordResponseSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)
    password = serializers.CharField(required=True, min_length=8, write_only=True)

    def validate_password(self, value):
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(e.messages)
        return value

class RecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recommendation
        fields = ['id', 'user', 'more_recommend', 'less_recommend', 'created_at', 'updated_at']

class FollowingSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='followee.id')
    username = serializers.ReadOnlyField(source='followee.username')
    first_name = serializers.ReadOnlyField(source='followee.first_name')
    last_name = serializers.ReadOnlyField(source='followee.last_name')
    middle_name = serializers.ReadOnlyField(source='followee.middle_name')
    email = serializers.ReadOnlyField(source='followee.email')
    avatar = serializers.ImageField(source='followee.avatar')

    class Meta:
        model = Follow
        fields = ['id', 'username', 'first_name', 'last_name', 'middle_name', 'email', 'avatar']


class FollowerSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='follower.id')
    username = serializers.ReadOnlyField(source='follower.username')
    first_name = serializers.ReadOnlyField(source='follower.first_name')
    last_name = serializers.ReadOnlyField(source='follower.last_name')
    middle_name = serializers.ReadOnlyField(source='follower.middle_name')
    email = serializers.ReadOnlyField(source='follower.email')
    avatar = serializers.ImageField(source='follower.avatar')

    class Meta:
        model = Follow
        fields = ['id', 'username', 'first_name', 'last_name', 'middle_name', 'email', 'avatar']
