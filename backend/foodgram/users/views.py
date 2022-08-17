from django.shortcuts import get_object_or_404

from rest_framework import status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action, api_view
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from api.models import Follow

from .models import User
from .pagination import CustomPagination
from .permissions import IsOwnerOrAuthenticated
from .serializers import (PasswordSerializer, SubscribeSerializer,
                          UserCreateSerializer, UserGetTokenSerializer,
                          UserReadSerializer)


class UserCustomViewSet(viewsets.ModelViewSet):
    pagination_class = CustomPagination
    permission_classes = (AllowAny, IsOwnerOrAuthenticated)
    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.action in ['create']:
            return UserCreateSerializer
        return UserReadSerializer

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated])
    def me(self, request):
        instance = self.request.user
        serializer = UserReadSerializer(instance, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['post'],
            permission_classes=[IsAuthenticated])
    def set_password(self, request):
        user = self.request.user
        serializer = PasswordSerializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated],
            url_path='')
    def subscriptions(self, request):
        followings = User.objects.filter(following__user=self.request.user)
        page = self.paginate_queryset(followings)
        if page is not None:
            serializer = SubscribeSerializer(page, context={
                'request': self.request}, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = SubscribeSerializer(
            followings, many=True, context={
                'request': self.request,
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
        is_subscribed = Follow.objects.filter(
            user=self.request.user,
            author=author
        ).exists()
        if request.method == 'GET':
            if request.user == author:
                error = 'You can not subscribe to yourself'
            else:
                if not is_subscribed:
                    Follow.objects.create(
                        user=request.user, author=author
                    )
                    author = get_object_or_404(
                        self.get_queryset(), id=author_id
                    )
                    serializer = SubscribeSerializer(
                        author, context={
                            'request': self.request,
                        }
                    )
                    return Response(
                        serializer.data,
                        status=status.HTTP_201_CREATED
                    )
                error = 'You have already been subscribed to this author'
        elif request.method == 'DELETE':
            if is_subscribed:
                item = get_object_or_404(
                    Follow, user=request.user, author=author
                )
                item.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            error = 'You have been not subscribed to this author'
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
