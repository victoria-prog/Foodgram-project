
from api.models import Follow
from django.db.models import Count, Exists, OuterRef, Value
from django.db.models.fields import BooleanField
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action, api_view
from rest_framework.mixins import (DestroyModelMixin, ListModelMixin,
                                   RetrieveModelMixin)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import User
from .pagination import CustomPagination
from .permissions import IsOwnerOrAuthenticated
from .serializers import (PasswordSerializer, SubscribeSerializer,
                          UserCreateSerializer, UserGetTokenSerializer,
                          UserReadSerializer)


class ListRetrieveDestroyViewSet(
    ListModelMixin, viewsets.GenericViewSet,
    RetrieveModelMixin, DestroyModelMixin
):
    pass


class UserCustomViewSet(viewsets.ModelViewSet):
    pagination_class = CustomPagination
    permission_classes = (AllowAny, IsOwnerOrAuthenticated)

    def get_queryset(self):
        if self.request.user.is_authenticated:
            queryset = User.objects.annotate(
                is_subscribed=Exists(Follow.objects.filter(
                        user=self.request.user,
                        author=OuterRef('following__author'))
                )
            ).annotate(recipes_count=Count('recipes'))
        else:
            queryset = User.objects.annotate(
                is_subscribed=Value(
                    False, output_field=BooleanField()
                )
            )
        return queryset

    def get_serializer_class(self):
        if self.action in ['create']:
            return UserCreateSerializer
        return UserReadSerializer

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated])
    def me(self, request):
        instance = self.request.user
        serializer = UserReadSerializer(instance)
        return Response(serializer.data)

    @action(detail=False, methods=['post'],
            permission_classes=[IsAuthenticated])
    def set_password(self, request):
        user = self.request.user
        serializer = PasswordSerializer(user, data=request.data)
        if serializer.is_valid():
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated],
            url_path='')
    def subscriptions(self, request):
        followings = self.get_queryset().filter(
            is_subscribed=True
        )
        page = self.paginate_queryset(followings)
        if page is not None:
            serializer = SubscribeSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = SubscribeSerializer(
            followings, many=True, context={
                'data': request.query_params
            }
        )
        return Response(serializer.data)

    @action(
        detail=True,
        methods=['get', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, *args, **kwargs):
        author_id = self.kwargs.get('pk')
        author = get_object_or_404(self.get_queryset(), id=author_id)
        serializer = SubscribeSerializer(
            author, context={'data': request.query_params}
        )
        if request.method == 'GET':
            if request.user == author:
                error = 'Вы не можете подписаться на самого себя'
            else:
                if not author.is_subscribed:
                    Follow.objects.create(
                        user=request.user, author=author
                    )
                    author = get_object_or_404(
                        self.get_queryset(), id=author_id
                    )
                    serializer = SubscribeSerializer(author)
                    return Response(
                        serializer.data,
                        status=status.HTTP_201_CREATED
                    )
                error = 'Вы уже подписаны на этого автора'
        elif request.method == 'DELETE':
            if author.is_subscribed:
                item = get_object_or_404(
                    Follow, user=request.user, author=author
                )
                item.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            error = 'Вы не подписаны на этого автора'
        return Response(
            {"errors": error},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
def get_token(request):
    serializer = UserGetTokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.validated_data['user']
    token, created = Token.objects.get_or_create(user=user)
    return Response(
            {'auth_token': f'{token.key}'},
            status=status.HTTP_201_CREATED
    )
