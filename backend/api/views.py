from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.contrib.auth.hashers import check_password
from django_filters import rest_framework as filters
from django.conf import settings
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
)
from rest_framework.response import Response

from django.http import FileResponse
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from recipes.models import (
    Ingredient,
    FavoriteRecipe,
    Recipe,
    RecipeIngredient,
    Tag,
    ShoppingCart
)
from .serializers import (
    FavoriteRecipeSerializer,
    IngredientSerializer,
    RecipeListSerializer,
    RecipeAddSerializer,
    SubscriptionCreateSerializer,
    TagSerializer,
    CustomUserSerializer,
    CustomUserCreateSerializer,
    SubscriptionListSerializer,
    SetPasswordSerializer,
    ShoppingCartSerializer,
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

    def get_serializer_class(self):
        if self.request.method in ('GET',):
            return CustomUserSerializer
        return CustomUserCreateSerializer

    @action(
        detail=False,
        methods=('GET', ),
        permission_classes=(IsAuthenticated, )
    )
    def me(self, request, *args, **kwargs):
        serializer = CustomUserSerializer(self.request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SetPasswordViewSet(viewsets.ModelViewSet):

    permission_classes = (IsAuthenticated, )
    serializer_class = SetPasswordSerializer

    def update(self, request, *args, **kwargs):
        user = get_object_or_404(CustomUser, id=request.user.id)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid()
        cur_password = serializer.validated_data['current_password']
        new_password = serializer.validated_data['new_password']
        if check_password(cur_password, user.password):
            user.set_password(new_password)
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет тега."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет ингридиента."""
    queryset = Ingredient.objects.all()
    permission_classes = (AllowAny, )
    serializer_class = IngredientSerializer
    filter_backends = [IngredientSearchFilter]
    search_fields = ('^name',)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет рецепта."""
    queryset = Recipe.objects.all()
    serializer_class = RecipeListSerializer
    pagination_class = PageLimitPagination
    permission_classes = [isAdminOrAuthorOrReadOnly]
    filter_backends = [filters.DjangoFilterBackend]
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
        queryset = CustomUser.objects.filter(following__user=self.request.user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscriptionListSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class SubcribeViewSet(viewsets.ModelViewSet):
    """Вьюсет подписки и отписки."""
    serializer_class = SubscriptionCreateSerializer
    pagination_class = None
    permission_classes = [IsAuthenticated]

    def create(self, request, following_id):
        user = request.user
        following = get_object_or_404(CustomUser, pk=following_id)
        logger.debug(f'\n Get USER: {user} \n')
        logger.debug(f'\n Get FOLLOWING: {following} \n')
        serializer = self.get_serializer(
            data={
                'user': user.id,
                'following': following.id
            },
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, following_id):
        user = request.user
        following = get_object_or_404(CustomUser, pk=following_id)

        serializer = self.get_serializer(
            data={
                'user': user.id,
                'following': following.id
            },
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        request.user.follower.filter(following=following).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FavoriteViewSet(viewsets.ModelViewSet):
    """Вьсет добавления и удаления избранного."""
    queryset = Recipe.objects.all()
    serializer_class = FavoriteRecipeSerializer
    permission_classes = [isAdminOrAuthorOrReadOnly]

    def create(self, request, recipe_id):
        logger.debug(f'\n Get USER: {request.user} \n')
        serializer = self.get_serializer(
            data={
                'user': request.user.id,
                'recipe': recipe_id
            },
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )

    def destroy(self, request, recipe_id):
        get_object_or_404(Recipe, id=recipe_id)
        user_id = request.user.id
        serializer = self.get_serializer(
            data={
                'user': request.user.id,
                'recipe': recipe_id
            },
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)

        FavoriteRecipe.objects.filter(
            user__id=user_id,
            recipe__id=recipe_id
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShoppingCartViewSet(viewsets.ModelViewSet):
    """Вьюсет добавления и удаления из корзины."""
    pagination_class = PageLimitPagination
    queryset = ShoppingCart.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = ShoppingCartSerializer

    def create(self, request, recipe_id):
        user = request.user
        logger.debug(f'\n Get USER: {user} \n')
        logger.debug(f'\n Get RECIPE_ID: {recipe_id} \n')
        serializer = self.get_serializer(
            data={
                'user': user.id,
                'recipe': recipe_id
            },
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, recipe_id):

        get_object_or_404(ShoppingCart, recipe_id=recipe_id)

        serializer = self.get_serializer(
            data={
                'user': request.user.id,
                'recipe': recipe_id
            },
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)

        ShoppingCart.objects.filter(
            user__id=request.user.id,
            recipe__id=recipe_id
        ).delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class DownloadShoppingCartViewset(viewsets.ModelViewSet):
    """Вьюсет скачивания списка покупок."""
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=A4)

        pdfmetrics.registerFont(
            TTFont(
                'Arial',
                str(settings.BASE_DIR / 'data/ArialRegular.ttf')
            )
        )
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
