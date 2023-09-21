from django_filters import rest_framework as filters
from recipes.models import Ingredient
from django_filters import AllValuesMultipleFilter
from django_filters.rest_framework import BooleanFilter, FilterSet

from recipes.models import Recipe


class IngredientSearchFilter(filters.FilterSet):
    """Фильтр для ингредиентов."""
    # name = filters.CharFilter(lookup_expr='istartswith')
    name = filters.CharFilter(method='filter_startwith_and_contains')

    class Meta:
        model = Ingredient
        fields = ['name']

    def filter_startwith_and_contains(self, queryset, name, value):
        starts_with_queryset = queryset.filter(name__startswith=value)
        contains_queryset = queryset.filter(name__contains=value)
        return starts_with_queryset.union(contains_queryset)


class RecipeFilterBackend(FilterSet):
    """Фильтр рецепта."""

    tags = AllValuesMultipleFilter(
        field_name="tags__slug",
    )
    is_favorited = BooleanFilter(
        method="filter_is_favorited",
    )
    is_in_shopping_cart = BooleanFilter(
        method="filter_is_in_shopping_cart",
    )

    class Meta:
        model = Recipe
        fields = ("tags", "author", "is_favorited", "is_in_shopping_cart")

    def filter_is_favorited(self, queryset, name, value):
        """Фильтрация рецептов в избранном."""
        if value:
            return queryset.filter(
                favorite_list_recipe__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        """Фильтрация рецептов в списке покупок."""
        if value:
            return queryset.filter(
                shopping_cart_recipe__user=self.request.user)
        return queryset
