from django.shortcuts import get_object_or_404

from rest_framework import serializers
from rest_framework.relations import PrimaryKeyRelatedField

from users.models import User

from .fields import Base64ImageField
from .models import (FavoriteRecipes, Follow, Ingredient, Recipe,
                     ShopCartRecipes, Tag)


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = Tag


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('id', 'name', 'measurement_unit')
        model = Ingredient


class IngredientForRecipeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        fields = '__all__'
        model = Ingredient
        read_only_fields = ('name', 'measurement_unit')


class UserForReciperializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'email', 'id', 'username', 'first_name', 'last_name'
        ]


class ShopFavorSerializer(serializers.ModelSerializer):
    image = Base64ImageField(
        max_length=None, use_url=True
    )

    class Meta:
        fields = ('id', 'name', 'image',  'cooking_time')
        model = Recipe
        read_only_fields = ('id', 'name', 'image', 'cooking_time')


class RecipeSerializer(serializers.ModelSerializer):
    tags = PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
    )
    ingredients = IngredientForRecipeSerializer(many=True)
    author = UserForReciperializer(read_only=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
    image = Base64ImageField(
        max_length=None, use_url=True
    )

    class Meta:
        fields = (
            'id', 'tags', 'author', 'ingredients',
            'is_favorited', 'is_in_shopping_cart',
            'name', 'image', 'text', 'cooking_time',

        )
        model = Recipe

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return ShopCartRecipes.objects.filter(
                user=user, recipe=obj
            ).exists()
        return False

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return FavoriteRecipes.objects.filter(
                user=user, recipe=obj
            ).exists()
        return False

    def to_representation(self, instance):
        representation = super(
            RecipeSerializer, self
        ).to_representation(instance)
        serializer = TagSerializer(instance.tags, many=True)
        representation['tags'] = serializer.data
        if self.context['request'].user.is_authenticated:
            is_subscribed = Follow.objects.filter(
                user=self.context['request'].user, author=instance.author
            ).exists()
        else:
            is_subscribed = False
        representation['author']['is_subscribed'] = is_subscribed
        return representation

    def create_or_update_ingredient(self, ingredients_data, tags, recipe):
        for ingredient in ingredients_data:
            new_ingredient = get_object_or_404(Ingredient, id=ingredient['id'])
            new_ingredient.amount = ingredient['amount']
            new_ingredient.save()
            recipe.ingredients.add(new_ingredient)
        for tag in tags:
            recipe.tags.add(tag)
        return recipe

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        return self.create_or_update_ingredient(ingredients_data, tags, recipe)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        instance.image = validated_data.get('image', instance.image)
        instance.save()
        ingredients_data = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance.ingredients.clear()
        instance.tags.clear()
        return self.create_or_update_ingredient(
            ingredients_data, tags, instance
        )

    def validate(self, data):
        ingredients_ids = Ingredient.objects.all().values_list(
            'id', flat=True
        )
        ingredients_list = [
            ingredient['id'] for ingredient in data['ingredients']
        ]
        if len(ingredients_list) > len(set(ingredients_list)):
            raise serializers.ValidationError(
                    'Такой ингредиент уже существует'
            )
        if not data['ingredients']:
            raise serializers.ValidationError(
                'Вы должны добавить хотя бы один ингредиент')
        for ingredient in data['ingredients']:
            print(ingredient)
            if ingredient['id'] not in ingredients_ids:
                raise serializers.ValidationError(
                    'Такого ингредиента не существует'
                )
            print(type(ingredient['amount']))
            if ingredient['amount'] <= 0:
                raise serializers.ValidationError(
                    'Количество ингредиантов не может быть меньше 1'
                )
        return data
