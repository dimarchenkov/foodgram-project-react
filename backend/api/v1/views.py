from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django_filters import rest_framework as filters
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from users.models import Subscription
from recipes.models import (
    Ingredient,
    Recipe,
    ShoppingCart,
    Tag,
    FavoriteRecipe
)
from api.v1.serializers import (
    SubscriptionSerializer,
    IngredientSerializer,
    RecipeSerializer,
    RecipeMinifiedSerializer,
    TagSerializer,
    UserSerializer
)
from api.v1.paginators import PageLimitPagination
from api.v1.filters import IngredientSearchFilter, RecipeFilterBackend
from api.v1.permissions import isAdminOrAuthorOrReadOnly


User = get_user_model()


class UserViewSet(UserViewSet):
    """Вьюсет юзера."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = PageLimitPagination
    permission_classes = [IsAuthenticated]

    @action(detail=False, url_path='subscriptions',
            url_name='subscriptions', permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        user = request.user
        queryset = user.subscribers.all()
        pages = self.paginate_queryset(queryset)
        serializer = SubscriptionSerializer(
            pages, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(methods=['post', 'delete'], detail=True, url_path='subscribe',
            url_name='subscribe', permission_classes=[IsAuthenticated])
    def subscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(User, id=id)
        if user == author:
            return Response(
                {'errors': 'На себя нельзя подписаться / отписаться'},
                status=status.HTTP_400_BAD_REQUEST)
        subscription = Subscription.objects.filter(
            author=author, user=user)
        if request.method == 'POST':
            if subscription.exists():
                return Response(
                    {'errors': 'Нельзя подписаться повторно'},
                    status=status.HTTP_400_BAD_REQUEST)
            queryset = Subscription.objects.create(author=author, user=user)
            serializer = SubscriptionSerializer(
                queryset, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            if not subscription.exists():
                return Response(
                    {'errors': 'Нельзя отписаться повторно'},
                    status=status.HTTP_400_BAD_REQUEST)
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class TagViewSet(viewsets.ModelViewSet):
    """Вьюсет тега."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = [AllowAny]


class IngredientViewSet(viewsets.ModelViewSet):
    """Вьюсет ингридиента."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = IngredientSearchFilter
    pagination_class = None
    permission_classes = [AllowAny]


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет рецепта."""
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = PageLimitPagination
    permission_classes = [isAdminOrAuthorOrReadOnly]
    filter_class = [RecipeFilterBackend]
    filter_backends = [filters.DjangoFilterBackend]
    pagination_class = PageLimitPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def add(self, model, user, pk, name):
        """Добавление рецепта в список пользователя."""
        recipe = get_object_or_404(Recipe, pk=pk)
        relation = model.objects.filter(user=user, recipe=recipe)
        if relation.exists():
            return Response(
                {'errors': f'Нельзя повторно добавить рецепт в {name}'},
                status=status.HTTP_400_BAD_REQUEST)
        model.objects.create(user=user, recipe=recipe)
        serializer = RecipeMinifiedSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_relation(self, model, user, pk, name):
        """Удаление рецепта из списка пользователя."""
        recipe = get_object_or_404(Recipe, pk=pk)
        relation = model.objects.filter(user=user, recipe=recipe)
        if not relation.exists():
            return Response(
                {'errors': 'Такой рецепт уже существует!'},
                status=status.HTTP_400_BAD_REQUEST)
        relation.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['post', 'delete'], detail=True, url_path='favorite',
            url_name='favorite')
    def favorite(self, request, pk=None):
        """Добавление и удаление рецептов - Избранное."""
        user = request.user
        if request.method == 'POST':
            name = 'избранное'
            return self.add(FavoriteRecipe, user, pk, name)
        if request.method == 'DELETE':
            name = 'избранного'
            return self.delete_relation(FavoriteRecipe, user, pk, name)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(methods=['post', 'delete'], detail=True, url_path='shopping_cart',
            url_name='shopping_cart')
    def shopping_cart(self, request, pk=None):
        """Добавление и удаление рецептов - Список покупок."""
        user = request.user
        if request.method == 'POST':
            name = 'список покупок'
            return self.add(ShoppingCart, user, pk, name)
        if request.method == 'DELETE':
            name = 'списка покупок'
            return self.delete_relation(ShoppingCart, user, pk, name)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)