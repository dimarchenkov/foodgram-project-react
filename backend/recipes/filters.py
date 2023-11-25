from rest_framework import filters

from django_filters.rest_framework import FilterSet
from django_filters.rest_framework import filters as djangofilters

from recipes.models import Ingredient, Tag, Recipe


class IngredientSearchFilter(filters.SearchFilter):
    name = djangofilters.CharFilter(lookup_expr='startswith')

    class Meta:
        model = Ingredient
        fields = ('name', )


class RecipeFilterBackend(FilterSet):
    is_favorited = djangofilters.BooleanFilter(
        method='get_favorite_recipes'
    )
    is_in_shopping_cart = djangofilters.BooleanFilter(
        method='get_is_in_shopping_cart'
    )
    tags = djangofilters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )

    class Meta:
        model = Recipe
        fields = (
            'author',
            'is_favorited',
            'is_in_shopping_cart',
            'tags'
        )

    def get_is_in_shopping_cart(self, queryset, name, value):
        if value:
            return queryset.filter(
                shopping_cart_recipes__user=self.request.user
            )
        return queryset

    def get_favorite_recipes(self, queryset, name, value):
        if value:
            return queryset.filter(favoriterecipe__user=self.request.user)
        return queryset
