"""Модуль серелизаторов.
"""
import logging
from django.contrib.auth import get_user_model
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import (
    Ingredient,
    Recipe,
    RecipeIngredient,
    Tag,
    ShoppingCart
)

logger = logging.getLogger(__name__)
CustomUser = get_user_model()


class CustomUserSerializer(serializers.ModelSerializer):

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'password'
        )
        extra_kwargs = {'password': {'write_only': True}}

    def get_is_subscribed(self, obj):
        req = self.context.get('request')
        logger.debug(f'obj: {obj}')
        logger.debug(f'req: {req}')
        if not req:
            return False
        if req.user.is_anonymous:
            return False
        return req.user.follower.filter(user=obj).exists()

    def create(self, validated_data):
        user = CustomUser(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug',
        )


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
        )


class RecipeIngredientAmountSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount'
        )


class AddIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(min_value=1)

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'amount'
        )


class RecipeListSerializer(serializers.ModelSerializer):

    author = CustomUserSerializer(
        read_only=True
    )
    tags = TagSerializer(
        many=True,
        read_only=True,
    )
    ingredients = RecipeIngredientAmountSerializer(
        many=True,
        source='recipe'
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def get_is_favorited(self, obj):
        req = self.context.get('request')
        logger.debug(f'obj: {obj}')
        logger.debug(f'req: {req}')
        if not req:
            return False
        if req.user.is_anonymous:
            return False
        return req.user.favorite_recipes.filter(recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        req = self.context.get('request')
        logger.debug(f'obj: {obj}')
        logger.debug(f'req: {req}')
        if not req:
            return False
        if req.user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            user=req.user,
            recipe=obj
        ).exists()


class RecipeAddSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(
        read_only=True
    )
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
    )
    ingredients = AddIngredientSerializer(
        many=True,
    )
    image = Base64ImageField()
    cooking_time = serializers.IntegerField(
        min_value=1,
        max_value=32000
    )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time'
        )

    def validate(self, attrs):
        tags = attrs.get('tags')
        logger.debug(tags)
        if not tags:
            raise serializers.ValidationError(
                {'tags': 'Необходимо указать минимум один тег'}
            )
        if len(tags) != len(set(tags)):
            raise serializers.ValidationError(
                {'tags': 'Теги не уникальны'}
            )

        if not attrs.get('ingredients'):
            raise serializers.ValidationError(
                {'ingredients': 'Необходимо выбрать ингредиенты'}
            )
        return attrs

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        request = self.context.get('request')
        recipe = Recipe.objects.create(
            author=request.user,
            **validated_data
        )
        return self._make_recipe(ingredients, recipe, tags)

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance.tags.clear()
        RecipeIngredient.objects.filter(recipe=instance).delete()

        super().update(instance, validated_data)

        return self._make_recipe(ingredients, instance, tags)

    def _make_recipe(self, ingredients, recipe, tags):
        RecipeIngredient.objects.bulk_create(
            RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient['id'],
                amount=ingredient['amount'],
            )
            for ingredient in ingredients
        )
        recipe.tags.set(tags)
        return recipe

    def to_representation(self, instance):
        return RecipeListSerializer(instance).data


class RecipeMinifiedSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )
        read_only_fields = (
            'name',
            'image',
            'cooking_time',
        )


class SubscriptionListSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.ReadOnlyField(source='recipes.count')

    class Meta:
        model = CustomUser
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )

    def get_is_subscribed(self, obj):
        req = self.context.get('request')
        logger.debug(f'obj: {obj}')
        logger.debug(f'req: {req}')
        if not req:
            return False
        if req.user.is_anonymous:
            return False
        return req.user.following.filter(following=obj).exists()

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes = obj.recipes.all()
        recipes_limit = request.query_params.get('recipes_limit')
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
        logger.debug(recipes)

        return RecipeMinifiedSerializer(
            recipes,
            many=True,
            context=self.context
        ).data