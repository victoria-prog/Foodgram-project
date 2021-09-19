from django_filters import rest_framework as filters

from .models import Ingredient, Recipe, Tag


class CustomSearchFilter(filters.FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug', to_field_name='slug',
        queryset=Tag.objects.all()
    )
    author = filters.CharFilter(field_name='author__id')
    is_in_shopping_cart = filters.BooleanFilter(method='shop_cart')
    is_favorited = filters.BooleanFilter(method='favorite')

    class Meta:
        model = Recipe
        fields = ['tags', 'author', 'is_in_shopping_cart', 'is_favorited']

    def shop_cart(self, queryset, name, value):
        if self.request.user.is_authenticated:
            if name and value:
                queryset = queryset.filter(
                    shop_cart__user=self.request.user
                )
        print(self.request.user, queryset.all())
        return queryset

    def favorite(self, queryset, name, value):
        if self.request.user.is_authenticated:
            if name and value:
                queryset = queryset.filter(
                    fav_recipes__user=self.request.user
                )
        return queryset


class CustomIngredientFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = Ingredient
        fields = ['name']
