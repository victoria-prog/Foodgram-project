
from api.models import Follow
from api.serializers import ShopFavorSerializer
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions as django_exceptions
from djoser.conf import settings
from djoser.serializers import UserSerializer
from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from .models import User


class UserCreateSerializer(UserSerializer):

    class Meta:
        model = User
        fields = [
            'email', 'id', 'username', 'first_name',
            'last_name', 'password'
        ]
        extra_kwargs = {
            'password': {
                'write_only': True
            }
        }

    def create(self, validated_data):
        username = self.validated_data['username']
        email = self.validated_data['email']
        first_name = self.validated_data['first_name']
        last_name = self.validated_data['last_name']
        password = self.validated_data['password']
        user_obj = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name
        )
        user_obj.set_password(password)
        user_obj.save()
        return user_obj


class UserReadSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed'
        ]

    def get_is_subscribed(self, obj):
        print(self)
        if self.context['request'].user.is_authenticated:
            return Follow.objects.filter(
                user=self.context['request'].user, author=obj
            ).exists()
        return False


class SubscribeSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed', 'recipes',
            'recipes_count'
        ]

    def get_is_subscribed(self, obj):
        return UserReadSerializer.get_is_subscribed(self, obj)

    def get_recipes_count(self, obj):
        return obj.recipes.all().count()

    def get_recipes(self, obj):
        count = 5
        try:
            count = int(self.context['request'].query_params['recipes_limit'])
            print(count)
        except Exception:
            pass
        print(obj.recipes.all())
        qs = obj.recipes.all()[:count]
        print(qs)
        serializer = ShopFavorSerializer(qs, many=True)
        return serializer.data


class UserGetTokenSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        if email and password:
            user = get_object_or_404(User, email=email)
            if not user:
                msg = 'Неверные учетные данные'
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = 'Поля "почта" и "пароль" обязательны для заполнения'
            raise serializers.ValidationError(msg, code='authorization')
        data['user'] = user
        return data


class PasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(style={"input_type": "password"})
    current_password = serializers.CharField(style={"input_type": "password"})

    default_error_messages = {
        "invalid_password": settings.CONSTANTS.messages.INVALID_PASSWORD_ERROR
    }

    def validate(self, data):
        user = self.instance
        current_password = data.get('current_password')
        is_password_valid = user.check_password(current_password)
        if is_password_valid:
            try:
                validate_password(data['new_password'], user)
            except django_exceptions.ValidationError as e:
                raise serializers.ValidationError(
                    {'new_password': list(e.messages)}
                )
            return data
        else:
            self.fail('invalid_password')
