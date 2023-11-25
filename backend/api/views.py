from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django_filters import rest_framework as filters
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAdminUser,
)
from rest_framework.response import Response

from django.http import FileResponse
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from users.models import Subscription
from recipes.models import (
    Ingredient,
    FavoriteRecipe,
    Recipe,
    RecipeIngredient,
    Tag,
    ShoppingCart
)
from .serializers import (
    IngredientSerializer,
    RecipeListSerializer,
    RecipeAddSerializer,
    RecipeMinifiedSerializer,
    TagSerializer,
    CustomUserSerializer,
    SubscriptionListSerializer,
)
from .paginators import PageLimitPagination
from .permissions import isAdminOrAuthorOrReadOnly
from recipes.filters import IngredientSearchFilter, RecipeFilterBackend
import logging


CustomUser = get_user_model()

logger = logging.getLogger(__name__)


class CustomUserViewSet(viewsets.ModelViewSet):
    """Вьюсет юзера."""
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    pagination_class = PageLimitPagination

    @action(
        detail=False,
        methods=('GET', ),
        permission_classes=(IsAuthenticated, )
    )
    def me(self, request, *args, **kwargs):
        if self.request.user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        serializer = self.get_serializer(self.request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет тега."""
    queryset = Tag.objects.all()
    logger.debug(f'queryset: {queryset}')
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет ингридиента."""
    queryset = Ingredient.objects.all()
    permission_classes = (AllowAny, )
    serializer_class = IngredientSerializer
    filter_backends = (IngredientSearchFilter, )
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет рецепта."""
    queryset = Recipe.objects.all()
    serializer_class = RecipeListSerializer
    pagination_class = PageLimitPagination
    permission_classes = (isAdminOrAuthorOrReadOnly, )
    filter_backends = (filters.DjangoFilterBackend, )
    filterset_class = RecipeFilterBackend

    def get_serializer_class(self):
        if self.action in ('list', 'retrive'):
            return RecipeListSerializer
        return RecipeAddSerializer


class SubsciptionsViewSet(viewsets.ModelViewSet):
    """Вьюсет отображения подписок."""
    serializer_class = SubscriptionListSerializer
    pagination_class = PageLimitPagination

    def list(self, request):
        logger.debug('You in func list')

        queryset = CustomUser.objects.filter(following__user=self.request.user)
        pages = self.paginate_queryset(queryset)

        logger.debug(f'queryset: {queryset}')

        serializer = SubscriptionListSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        print(serializer.data)
        return self.get_paginated_response(serializer.data)


class SubcribeViewSet(viewsets.ModelViewSet):
    """Вьюсет подписки и отписки."""
    pagination_class = None
    permission_classes = [IsAdminUser | IsAuthenticated]

    def create(self, request, user_id):
        logger.debug(f'user_id {user_id}')

        user = get_object_or_404(CustomUser, id=user_id)
        subscribe = Subscription.objects.create(
            user=request.user,
            following=user)
        serializer = RecipeMinifiedSerializer(
            subscribe,
            context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, user_id):
        logger.debug(f'user_id {user_id}')
        following = get_object_or_404(CustomUser, pk=user_id)
        request.user.follower.filter(following=following).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FavoriteViewSet(viewsets.ModelViewSet):
    """Вьсет добавления и удаления избранного."""
    queryset = Recipe.objects.all()
    serializer_class = RecipeMinifiedSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        logger.debug(request)
        recipe = get_object_or_404(Recipe, id=self.kwargs['id'])
        serializer = self.get_serializer(
            request.user.favorite_recipes.create(recipe=recipe)
        )
        return Response(
            serializer.to_representation(instance=recipe),
            status=status.HTTP_201_CREATED,
        )

    def destroy(self, request,  *args, **kwargs):
        recipe = get_object_or_404(Recipe, id=self.kwargs['id'])
        user_id = request.user.id
        logger.debug(f'recipe id: {recipe.id}, user id: {user_id}')
        FavoriteRecipe.objects.filter(
            user__id=user_id,
            recipe__id=recipe.id
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShoppingCartViewSet(viewsets.ModelViewSet):
    """Вьюсет добавления и удаления из корзины"""
    pagination_class = PageLimitPagination
    queryset = ShoppingCart.objects.all()
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        recipe_id = self.kwargs["id"]
        recipe = get_object_or_404(Recipe, id=recipe_id)
        ShoppingCart.objects.create(user=request.user, recipe=recipe)
        serializer = RecipeMinifiedSerializer()
        return Response(
            serializer.to_representation(instance=recipe),
            status=status.HTTP_201_CREATED,
        )

    def destroy(self, request, *args, **kwargs):
        recipe_id = self.kwargs['id']
        user_id = request.user.id
        ShoppingCart.objects.filter(
            user__id=user_id,
            recipe__id=recipe_id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class DownloadShoppingCartViewset(viewsets.ModelViewSet):
    """Вьюсет скачивания списка покупок."""
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)

        pdfmetrics.registerFont(TTFont('Arial', '/app/data/ArialRegular.ttf'))
        p.setFont('Arial', 16)
        x, y = 100, 750

        ingredients = RecipeIngredient.objects.filter(
            recipe__shopping_cart_recipes__user=request.user
        ).values_list(
            'ingredient__name',
            'ingredient__measurement_unit',
            'amount'
        )

        for ingredient in ingredients:
            text = (f'{ingredient[0]} {ingredient[2]} {ingredient[1]}')
            p.drawString(x, y, text)
            y -= 24

        p.showPage()
        p.save()
        buffer.seek(0)
        response = FileResponse(
            buffer,
            as_attachment=True,
            filename='shopping_cart.pdf',
        )

        return response
