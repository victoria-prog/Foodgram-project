from django.contrib import admin

from .models import (FavoriteRecipes, Follow, Ingredient, Recipe,
                     ShopCartRecipes, Tag)


class RecipeAdmin(admin.ModelAdmin):

    list_display = (
        'name', 'author', 'amount_of_adding_to_favorite'
    )
    search_fields = ('name', 'author__username', 'tags__name')
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'

    def amount_of_adding_to_favorite(self, obj):
        return obj.fav_recipes.count()


class TagAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
    list_display = ('pk', 'name', 'color')


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)


class FollowAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'author')


class ShopCartRecipesAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'user')


class FavoriteRecipesAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'user')


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Follow, FollowAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(FavoriteRecipes, FavoriteRecipesAdmin)
admin.site.register(ShopCartRecipes, ShopCartRecipesAdmin)
