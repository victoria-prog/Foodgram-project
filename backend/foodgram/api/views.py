from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from users.pagination import CustomPagination

from .filters import CustomIngredientFilter, CustomSearchFilter
from .mixins import ListRetrieveViewSet
from .models import FavoriteRecipes, Ingredient, Recipe, ShopCartRecipes, Tag
from .permissions import OwnerOrReadonly
from .serializers import (IngredientSerializer, RecipeSerializer,
                          ShopFavorSerializer, TagSerializer)


class IngredientViewSet(ListRetrieveViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = CustomIngredientFilter
    filterset_fields = ['name']


class TagViewSet(ListRetrieveViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)


class RecipeViewSet(viewsets.ModelViewSet):
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, OwnerOrReadonly,)
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = CustomSearchFilter
    queryset = Recipe.objects.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True,
            methods=['get', 'delete'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, *args, **kwargs):
        recipe_id = self.kwargs.get('pk')
        recipe = get_object_or_404(self.get_queryset(), id=recipe_id)
        serializer = ShopFavorSerializer(recipe)
        is_in_shopping_cart = ShopCartRecipes.objects.filter(
            user=self.request.user, recipe=recipe
        ).exists()
        if request.method == 'GET':
            if not is_in_shopping_cart:
                ShopCartRecipes.objects.create(
                    user=request.user, recipe=recipe
                )
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )
            return Response(
                {"errors": "Рецепт уже в корзине"},
                status=status.HTTP_400_BAD_REQUEST
            )
        elif request.method == 'DELETE':
            if is_in_shopping_cart:
                item = get_object_or_404(
                    ShopCartRecipes, user=request.user, recipe=recipe
                )
                item.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {"errors": "Рецепта в корзине нет"},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True,
            methods=['get', 'delete'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, *args, **kwargs):
        recipe_id = self.kwargs.get('pk')
        recipe = get_object_or_404(self.get_queryset(), id=recipe_id)
        serializer = ShopFavorSerializer(recipe)
        is_favorite = FavoriteRecipes.objects.filter(
            user=self.request.user, recipe=recipe
        ).exists()
        if request.method == 'GET':
            if not is_favorite:
                FavoriteRecipes.objects.create(
                    user=request.user, recipe=recipe
                )
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )
            return Response(
                {"errors": "Рецепт уже в избранном"},
                status=status.HTTP_400_BAD_REQUEST
            )
        elif request.method == 'DELETE':
            if is_favorite:
                item = get_object_or_404(
                    FavoriteRecipes, user=request.user, recipe=recipe
                )
                item.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {"errors": "Рецепта нет в избранном"},
                status=status.HTTP_400_BAD_REQUEST
            )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download(request):
    qs = Recipe.objects.filter(shop_cart__user=request.user)
    cart = {}
    ingredients = Ingredient.objects.filter(
        id__in=qs.values_list('ingredients', flat=True)
    )
    for ingredient in ingredients:
        key = f'{ingredient.name}, {ingredient.measurement_unit}'
        cart[key] = cart.get(
            key, 0
        ) + ingredient.amount
    text_data = ""
    for name, amount in cart.items():
        string = f'{name} - {amount}'.format(name, amount)
        text_data += string + '\n'
    response = HttpResponse(text_data, content_type='text')
    response['Content-Disposition'] = 'attachment;'
    return response
