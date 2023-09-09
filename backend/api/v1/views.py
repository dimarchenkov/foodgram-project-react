from io import StringIO

from django.db.models import Sum
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from api.v1.serializers import SetPasswordSerializer
from recipes.models import (
    Ingredient,
    FavoriteRecipe,
    RecipeIngredient,
    Recipe,
    ShoppingList,
    Tag
)
from users.models import Follow

from api.v1.filters import (
    IngredientSearchFilterBackend,
    RecipeFilterBackend
)
from api.v1.permissions import RecipePermission
from api.v1.serializers import (
    FollowSerializer,
    RecipeSerializer,
    IngredientSerializer,
    RecipeCreateSerializer,
    RecipeShortSerializer,
    TagSerializer,
    UserCreateSerializer,
    UserSerializer
)
from api.v1.mixins import CreateRetriveListViewSet, RetriveListViewSet

# from .utils import PageLimitPaginator, delete_old_ingredients


User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """Вьюсет пользователя."""
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    pagination_class = PageNumberPagination

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return UserSerializer
        return UserCreateSerializer

    @action(detail=False, methods=['post'],
            permission_classes=(AllowAny,))
    def signup(self, request):
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'],
            pagination_class=None,
            permission_classes=(IsAuthenticated,))
    def me(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data,
                        status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'],
            permission_classes=(IsAuthenticated,))
    def set_password(self, request):
        serializer = SetPasswordSerializer(request.user, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response({'detail': 'Пароль успешно изменен'},
                        status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(IsAuthenticated,),
        pagination_class=PageNumberPagination
    )
    def subscriptions(self, request):
        queryset = User.objects.filter(subscribing__user=request.user)
        pages = self.paginate_queryset(queryset)
        serializer = FollowSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, **kwargs):
        author = get_object_or_404(User, id=kwargs['pk'])
        serializer = FollowSerializer(
            author,
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.create(request.user, author)
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def unsubscribe(self, request, **kwargs):
        author = get_object_or_404(User, id=kwargs['pk'])
        get_object_or_404(
            Follow,
            user=request.user,
            author=author
        ).delete()
        return Response({'detail': 'Успешная отписка'},
                        status=status.HTTP_204_NO_CONTENT)


class FollowViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)

    def create(self, request, user_id):
        follow_author = get_object_or_404(User, pk=user_id)
        if follow_author != request.user and (
            not request.user.follower.filter(author=follow_author).exists()
        ):
            Follow.objects.create(
                user=request.user,
                author=follow_author
            )
            serializer = FollowSerializer(
                follow_author, context={'request': request}
            )
            return Response(serializer.data, status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, user_id):
        follow_author = get_object_or_404(User, pk=user_id)
        data_follow = request.user.follower.filter(author=follow_author)
        if data_follow.exists():
            data_follow.delete()
            return Response(status.HTTP_204_NO_CONTENT)
        return Response(status.HTTP_400_BAD_REQUEST)


class TagViewSet(viewsets.ModelViewSet):
    """Вьюсет тега."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ModelViewSet):
    """Вьюсет ингридиента."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (IngredientSearchFilterBackend,)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет рецепта."""
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = PageNumberPagination
    # permission_classes = (RecipePermission,)
    permission_classes = (AllowAny,)
    filter_backends = (RecipeFilterBackend,)

    def get_serializer_class(self):
        if self.action in ['create', 'partial_update']:
            return RecipeCreateSerializer
        return RecipeSerializer

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=(permissions.IsAuthenticated,),
    )
    def download_shopping_cart(self, request):
        shopping_list = RecipeIngredient.objects.filter(
            recipes__shopping_list_recipes__user=request.user
        )
        shopping_list = shopping_list.values('ingredient').annotate(
            total_amount=Sum('amount')
        )
        shopping_cart_file = StringIO()
        for position in shopping_list:
            position_ingredient = get_object_or_404(
                Ingredient,
                pk=position['ingredient']
            )
            position_amount = position['total_amount']
            shopping_cart_file.write(
                f' *  {position_ingredient.name.title()}'
                f' ({position_ingredient.measurement_unit})'
                f' - {position_amount}' + '\n'
            )
        response = HttpResponse(
            shopping_cart_file.getvalue(),
            content_type='text'
        )
        response['Content-Disposition'] = (
            'attachment; filename="shopping_list.txt"'
        )
        return response


class CustomCreateAndDeleteMixin:
    def custom_create(self, request, id, attribute, model):
        recipe = get_object_or_404(Recipe, pk=id)
        queryset = getattr(recipe, attribute)
        if not queryset.filter(
            user=request.user
        ).exists():
            model.objects.create(
                user=request.user,
                recipe=recipe
            )
            serializer = RecipeShortSerializer(
                recipe, context={'request': request}
            )
            return Response(serializer.data, status.HTTP_201_CREATED)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def custom_destroy(self, request, id, attribute):
        recipe = get_object_or_404(Recipe, pk=id)
        queryset = getattr(recipe, attribute)
        data = (
            queryset.filter(
                user=request.user
            )
        )
        if data.exists():
            data.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class ShoppingCartViewSet(viewsets.ViewSet, CustomCreateAndDeleteMixin):
    permission_classes = (permissions.IsAuthenticated,)

    def create(self, request, id):
        attribute = 'shopping_list_recipes'
        model = ShoppingList
        return self.custom_create(request, id, attribute, model)

    def destroy(self, request, id):
        attribute = 'shopping_list_recipes'
        return self.custom_destroy(request, id, attribute)


class FavoriteViewSet(viewsets.ViewSet, CustomCreateAndDeleteMixin):
    permission_classes = (permissions.IsAuthenticated,)

    def create(self, request, id):
        attribute = 'favorite_recipes'
        model = FavoriteRecipe
        return self.custom_create(request, id, attribute, model)

    def destroy(self, request, id):
        attribute = 'favorite_recipes'
        return self.custom_destroy(request, id, attribute)
