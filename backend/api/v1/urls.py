"""
URL для API версии 1
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

# from .views import (IngredientViewSet, RecipeViewSet, TagViewSet,
#                   SubscriptionViewSet)
from api.v1.views import (
    IngredientViewSet,
    RecipeViewSet,
    TagViewSet,
    UserViewSet
)

v1_router = DefaultRouter()

v1_router.register('tags', TagViewSet)
v1_router.register('ingredients', IngredientViewSet)
v1_router.register('recipes', RecipeViewSet)
v1_router.register('users', UserViewSet)

urlpatterns = [
    path('', include(v1_router.urls)),
    path(r'auth/', include('djoser.urls.authtoken')),
]
