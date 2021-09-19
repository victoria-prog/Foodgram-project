from colorfield.fields import ColorField
from django.core.validators import MinValueValidator
from django.db import models
from users.models import User


class Tag(models.Model):
    name = models.CharField(
        max_length=200, verbose_name='Тег', unique=True
    )
    color = ColorField(
        max_length=7, default='#FF0000', unique=True, null=True
    )
    slug = models.SlugField(max_length=200, unique=True, null=True)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200, verbose_name='Ингредиент'
    )
    measurement_unit = models.CharField(
        max_length=200, verbose_name='Единица измерения'
    )
    amount = models.PositiveIntegerField(
        default=1, validators=[MinValueValidator(1)]
    )

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='recipes'
    )
    name = models.CharField(
        unique=True, max_length=200, verbose_name='Название рецепта'
    )
    image = models.ImageField(
        upload_to='recipes/images', verbose_name='Изображение'
    )
    text = models.TextField(verbose_name='Описание рецепта')
    ingredients = models.ManyToManyField(
        'Ingredient', verbose_name='Ингредиенты', related_name='recipe')
    tags = models.ManyToManyField(
        'Tag', verbose_name='Теги', related_name='recipe'
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления', validators=[MinValueValidator(1)]
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата добавления', auto_now_add=True
    )

    class Meta:
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name


class Follow(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='follower'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='following'
    )

    class Meta:
        constraints = [models.UniqueConstraint(
            fields=['user', 'author'], name="user-author"
            )
        ]

    def __str__(self):
        return f'Подписчик: {self.user}, Избранный автор: {self.author}'


class FavoriteRecipes(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='fav_recipes'
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='favorite'
    )

    class Meta:
        constraints = [models.UniqueConstraint(
            fields=['recipe', 'user'], name="fav_recipe-user"
            )
        ]

    def __str__(self):
        return f'Рецепт {self.recipe}, Подписчик: {self.user}'


class ShopCartRecipes(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='shop_cart'
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='cart'
    )

    class Meta:
        constraints = [models.UniqueConstraint(
            fields=['recipe', 'user'], name="cart_recipe-user"
            )
        ]

    def __str__(self):
        return f'Рецепт {self.recipe}, Подписчик: {self.user}'
