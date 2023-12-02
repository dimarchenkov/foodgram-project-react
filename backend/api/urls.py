"""
Модуль настройки URL для API.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    IngredientViewSet,
    RecipeViewSet,
    TagViewSet,
    CustomUserViewSet,
    SubsciptionsViewSet,
    SubcribeViewSet,
    FavoriteViewSet,
    ShoppingCartViewSet,
    DownloadShoppingCartViewset,
    SetPasswordViewSet
)

v1_router = DefaultRouter()

v1_router.register('tags', TagViewSet)
v1_router.register('ingredients', IngredientViewSet)
v1_router.register('recipes', RecipeViewSet)
v1_router.register('users', CustomUserViewSet)

urlpatterns = [
    path(
        'users/<int:following_id>/subscribe/',
        SubcribeViewSet.as_view({
            'post': 'create',
            'delete': 'destroy'
        }),
        name='subscribe'
    ),
    path(
        'users/subscriptions/',
        SubsciptionsViewSet.as_view({
            'get': 'list'
        }),
        name='subscriptions'
    ),
    path(
        'users/set_password/',
        SetPasswordViewSet.as_view({
            'post': 'update'
        }),
        name='set_password'
    ),
    path(
        'recipes/<int:recipe_id>/favorite/',
        FavoriteViewSet.as_view({
            'post': 'create',
            'delete': 'destroy'
        }),
        name='favorite'
    ),
    path(
        'recipes/<int:recipe_id>/shopping_cart/',
        ShoppingCartViewSet.as_view({
            'post': 'create',
            'delete': 'destroy'
        }),
        name='shopping_cart'
    ),
    path(
        'recipes/download_shopping_cart/',
        DownloadShoppingCartViewset.as_view({
            'get': 'list'
        }),
        name='download_shopping_cart'
    ),
    path('', include(v1_router.urls)),
    path(r'auth/', include('djoser.urls.authtoken')),
    path(r'auth/', include('djoser.urls')),
]
