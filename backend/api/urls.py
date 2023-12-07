"""
Модуль настройки URL для API.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CustomUserViewSet, IngredientViewSet, RecipeViewSet,
                    TagViewSet)

app_name = 'api'

v1_router = DefaultRouter()

v1_router.register('tags', TagViewSet)
v1_router.register('ingredients', IngredientViewSet)
v1_router.register('recipes', RecipeViewSet)
v1_router.register('users', CustomUserViewSet)

urlpatterns = [
    path('', include(v1_router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
    path('auth/', include('djoser.urls')),
]
