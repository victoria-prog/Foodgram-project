from django.urls import include, path
from rest_framework.routers import SimpleRouter

from . import views

app_name = 'api'


router = SimpleRouter()
router.register('recipes', views.RecipeViewSet, basename='recipes')
router.register('tags', views.TagViewSet, basename='tags')
router.register('ingredients', views.IngredientViewSet, basename='ingredients')


urlpatterns = [
    path('recipes/download_shopping_cart/', views.download),
    path('', include(router.urls)),
]
