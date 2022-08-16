from django.core.validators import MinValueValidator
from django.db import models

from colorfield.fields import ColorField

from users.models import User


class Tag(models.Model):
    name = models.CharField(
        max_length=200, verbose_name='Tag', unique=True
    )
    color = ColorField(
        max_length=7, default='#FF0000', unique=True, null=True,
        verbose_name='Color'
    )
    slug = models.SlugField(
        max_length=200, unique=True, null=True, verbose_name='Slug'
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200, verbose_name='Ingredient'
    )
    measurement_unit = models.CharField(
        max_length=200, verbose_name='Measurement unit'
    )
    amount = models.IntegerField(
        verbose_name='Quantity',
        default=1,
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ingredient'
        verbose_name_plural = 'Ingredients'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='recipes',
        verbose_name='Author'
    )
    name = models.CharField(
        unique=True, max_length=200, verbose_name='Recipe name'
    )
    image = models.ImageField(
        upload_to='recipes/images', verbose_name='Image'
    )
    text = models.TextField(verbose_name='Recipe description')
    ingredients = models.ManyToManyField(
        'Ingredient', verbose_name='Ingredients', related_name='recipes')
    tags = models.ManyToManyField(
        'Tag', verbose_name='Tags', related_name='recipes'
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Cooking time', validators=[MinValueValidator(1)]
    )
    pub_date = models.DateTimeField(
        verbose_name='Publication date', auto_now_add=True
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Recipe'
        verbose_name_plural = 'Recipes'

    def __str__(self):
        return self.name


class Follow(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='follower',
        verbose_name='Follower'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='following',
        verbose_name='Author'
    )

    class Meta:
        constraints = [models.UniqueConstraint(
            fields=['user', 'author'], name="user-author"
            )
        ]
        verbose_name = 'Following'
        verbose_name_plural = 'Followings'

    def __str__(self):
        return f'Follower: {self.user}, Favourite author: {self.author}'


class FavoriteRecipes(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='fav_recipes',
        verbose_name='Recipe'
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='favorite',
        verbose_name='Follower'
    )

    class Meta:
        constraints = [models.UniqueConstraint(
            fields=['recipe', 'user'], name="fav_recipe-user"
            )
        ]
        verbose_name = 'Favourite recipe'
        verbose_name_plural = 'Favourite recipes'

    def __str__(self):
        return f'Recipe {self.recipe}, Follower: {self.user}'


class ShopCartRecipes(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name='shop_cart',
        verbose_name='Recipe'
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='cart',
        verbose_name='Follower'
    )

    class Meta:
        constraints = [models.UniqueConstraint(
            fields=['recipe', 'user'], name="cart_recipe-user"
            )
        ]
        verbose_name = 'Cart'
        verbose_name_plural = 'Carts'

    def __str__(self):
        return f'Recipe {self.recipe}, Follower: {self.user}'
