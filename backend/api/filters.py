"""
Настройки фильтрации.
"""
from django_filters.rest_framework import FilterSet
from django_filters.rest_framework import filters as djangofilters
from rest_framework.filters import SearchFilter

from recipes.models import Ingredient, Recipe


class IngredientSearchFilter(SearchFilter):
    """
    A search filter that filters
    ingredients based on their name.

    Attributes:
        search_param (str): The query parameter
        name for specifying the search term.

    Meta:
        model (Ingredient): The model class to filter.
        fields (tuple): The fields to search for
        the specified search term (default='name').

    """
    search_param = 'name'

    class Meta:
        model = Ingredient
        fields = ('name', )


class RecipeFilterBackend(FilterSet):
    """
    A filter backend for recipes that allows filtering based on various
    criteria such as favorited recipes, recipes in shopping cart, and tags.

    Attributes:
        is_favorited (NumberFilter): Filter for favorited recipes.
        is_in_shopping_cart (NumberFilter): Filter for recipes
            in shopping cart.
        tags (AllValuesMultipleFilter): Filter for recipes
            with specific tags.

    Meta:
        model (class): The model class to filter.
        fields (tuple): The fields to filter on.

    Methods:
        get_is_in_shopping_cart(queryset, name, value): Filters the queryset
        based on whether the recipes are in the shopping cart of the
        authenticated user.
        get_favorite_recipes(queryset, name, value): Filters the queryset
        based on whether the recipes are favorited by the authenticated user.

    """

    is_favorited = djangofilters.NumberFilter(
        method='get_favorite_recipes'
    )
    is_in_shopping_cart = djangofilters.NumberFilter(
        method='get_is_in_shopping_cart'
    )
    tags = djangofilters.AllValuesMultipleFilter(
        field_name='tags__slug'
    )

    class Meta:
        model = Recipe
        fields = (
            'author',
            'is_favorited',
            'is_in_shopping_cart',
            'tags'
        )

    def get_is_in_shopping_cart(self, queryset, name, value) -> any:
        """
        Filters the queryset based on whether the recipes
        are in the shopping cart of the authenticated user.

        Args:
            self: The instance of the filter backend.
            queryset: The queryset to filter.
            name: The name of the filter.
            value: The value of the filter.

        Returns:
            QuerySet: The filtered queryset.
         """
        if value and self.request.user.is_authenticated:
            return queryset.filter(
                shopping_carts__user=self.request.user
            )
        return queryset

    def get_favorite_recipes(self, queryset, name, value) -> any:
        """
        Filters the queryset based on whether the recipes
        are favorited by the authenticated user.

        Args:
            self: The instance of the filter backend.
            queryset: The queryset to filter.
            name: The name of the filter.
            value: The value of the filter.

        Returns:
            QuerySet: The filtered queryset.
        """
        if value and self.request.user.is_authenticated:
            return queryset.filter(
                favorite_recipes__user=self.request.user
            )
        return queryset
