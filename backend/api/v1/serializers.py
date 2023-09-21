"""Модуль серелизаторов для api версии 1."""
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from djoser.serializers import UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from django.db.transaction import atomic

from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag

from api.v1.validators import validate_ingredients, validate_tags


User = get_user_model()


class UserSerializer(UserSerializer):
    """
    Сериализатор модели User.

    Атрибуты:
        is_subscribed (SerializerMethodField): поле метода сериализатора,
        позволяющее определить, подписан ли пользователь.

    Мета:
        model (User): Модель для сериализации.
        fields (tuple): поля, которые будут включены в
        сериализованное представление.
        extra_kwargs (dict): дополнительные аргументы
        ключевого слова для полей.

    Методы:
        get_is_subscribed(obj): возвращает логическое значение,
        указывающее, подписан ли пользователь.
        create(validated_data): Создает новый экземпляр пользователя
        на основе проверенных данных.
    """
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        """Класс Meta серелизатора UserSerializer."""
        model = User
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
        user = self.context.get('request').user
        return obj.subscribed.filter(user=user.id).exists()

    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user


class TagSerializer(serializers.ModelSerializer):
    """
    Серелизатор тегов.

    Meta:
        model (Tag): Модель серелизации.
        fields (tuple): поля, которые будут включены в
        сериализованное представление.
    """

    class Meta:
        """Класс Meta для TagSerializer."""
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug',
        )


class IngredientSerializer(serializers.ModelSerializer):
    """
    Сериализатор ингредиентов.

    Meta:
        model (Ingredient): Модель для сериализации.
        fields (tuple): поля, которые будут включены в
        сериализованное представление.
        read_only_fields (tuple): Поля read-only.
    """

    class Meta:
        """Класс Meta для IngredientSerializer."""
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
        )
        read_only_fields = (
            'id',
            'name',
            'measurement_unit',
        )


class RecipeIngredientAmountSerializer(serializers.ModelSerializer):
    """
    Сериализует количество ингредиентов рецепта.

    """
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


class RecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для рецептов.
    """
    author = UserSerializer(read_only=True)
    tags = TagSerializer(
        read_only=True,
        many=True
    )
    ingredients = RecipeIngredientAmountSerializer(
        read_only=True,
        many=True,
        source='ingredientamount_set'
    )
    image = Base64ImageField()
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
        """Рецепт в избранном или нет. """
        user = self.context.get('request').user
        if user.is_authenticated:
            return user.favorite_recipes.filter(recipe=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        """Рецепт в списке покупок."""
        user = self.context.get('request').user
        if user.is_authenticated:
            return user.shopping_cart.filter(recipe=obj).exists()
        return False

    def get_author(self, obj):
        """Рецепт в списке покупок."""
        user = self.context.get('request').user
        return user.recipe.all()

    def create_ingredient_amount(self, valid_ingredients, recipe):
        ingredient_amounts = []

        for ingredient_data in valid_ingredients:
            ingredient = get_object_or_404(
                Ingredient, id=ingredient_data.get('id'))
            ingredient_amount = RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient,
                amount=ingredient_data.get('amount'))
            ingredient_amounts.append(ingredient_amount)

        RecipeIngredient.objects.bulk_create(ingredient_amounts)

    def create_tags(self, data, recipe):
        """Создание тэгов у рецепта."""
        valid_tags = validate_tags(data.get('tags'))
        tags = Tag.objects.filter(id__in=valid_tags)
        recipe.tags.set(tags)

    def validate(self, data):
        """Валидация ингридиентов."""
        ingredients = self.initial_data.get('ingredients')
        valid_ingredients = validate_ingredients(ingredients)
        data['ingredients'] = valid_ingredients
        return data

    @atomic
    def create(self, validated_data):
        """Создание рецепта."""
        valid_ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        self.create_tags(self.initial_data, recipe)
        self.create_ingredient_amount(valid_ingredients, recipe)
        return recipe

    @atomic
    def update(self, instance, validated_data):
        instance.tags.clear()
        RecipeIngredient.objects.filter(recipe=instance).delete()
        instance.tags.set(validated_data.pop('tags'))
        ingredients = validated_data.pop('ingredients')
        self.create_ingredients(instance, ingredients)
        return super().update(instance, validated_data)


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


class SubscriptionSerializer(UserSerializer):
    """Серелизатор подписок."""
    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.ReadOnlyField(source='author.recipes.count')

    class Meta:
        model = User
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
        """Статус подписки на автора."""
        user = self.context.get('request').user
        return user.subscribers.filter(author=obj.author).exists()

    def get_recipes(self, obj):
        recipes_limit = (
            self.context['request'].query_params.get('recipes_limit')
        )
        recipes = obj.author.recipes.all()
        if recipes_limit is not None:
            recipes_limit = int(recipes_limit)
            serializer = RecipeMinifiedSerializer(
                recipes[:recipes_limit], many=True
            )
        else:
            serializer = RecipeMinifiedSerializer(recipes, many=True)
        return serializer.data
