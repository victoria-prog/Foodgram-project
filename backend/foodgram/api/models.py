from django.core.validators import MinValueValidator
from django.db import models

from colorfield.fields import ColorField

from users.models import User


class Tag(models.Model):
    name = models.CharField(
        max_length=200, verbose_name='Тег', unique=True
    )
    color = ColorField(
        max_length=7, default='#FF0000', unique=True, null=True,
        verbose_name='Цвет'
    )
    slug = models.SlugField(
        max_length=200, unique=True, null=True, verbose_name='Слаг'
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200, verbose_name='Ингредиент'
    )
    measurement_unit = models.CharField(
        max_length=200, verbose_name='Единица измерения'
    )
    amount = models.IntegerField(
        verbose_name='Количество',
        default=1,
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='recipes',
        verbose_name='Автор'
    )
    name = models.CharField(
        unique=True, max_length=200, verbose_name='Название рецепта'
    )
    image = models.ImageField(
        upload_to='recipes/images', verbose_name='Изображение'
    )
    text = models.TextField(verbose_name='Описание рецепта')
    ingredients = models.ManyToManyField(
        'Ingredient', verbose_name='Ингредиенты', related_name='recipes')
    tags = models.ManyToManyField(
        'Tag', verbose_name='Теги', related_name='recipes'
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления', validators=[MinValueValidator(1)]
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата добавления', auto_now_add=True
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class Follow(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='follower',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='following',
        verbose_name='Автор'
    )

    class Meta:
        constraints = [models.UniqueConstraint(
            fields=['user', 'author'], name="user-author"
            )
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'Подписчик: {self.user}, Избранный автор: {self.author}'


class FavoriteRecipes(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='fav_recipes',
        verbose_name='Рецепт'
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='favorite',
        verbose_name='Подписчик'
    )

    class Meta:
        constraints = [models.UniqueConstraint(
            fields=['recipe', 'user'], name="fav_recipe-user"
            )
        ]
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'

    def __str__(self):
        return f'Рецепт {self.recipe}, Подписчик: {self.user}'


class ShopCartRecipes(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='shop_cart',
        verbose_name='Рецепт'
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='cart',
        verbose_name='Подписчик'
    )

    class Meta:
        constraints = [models.UniqueConstraint(
            fields=['recipe', 'user'], name="cart_recipe-user"
            )
        ]
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'

    def __str__(self):
        return f'Рецепт {self.recipe}, Подписчик: {self.user}'
