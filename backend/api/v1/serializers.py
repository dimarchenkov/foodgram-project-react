
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from recipes.models import RecipeIngredient, Ingredient, Recipe, Tag
from rest_framework import serializers
from djoser.serializers import UserSerializer
from users.models import Follow
from api.v1.utils import Base64ImageField
# from .utils import delete_old_ingredients
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions as django_exceptions


User = get_user_model()


class UserSerializer(UserSerializer):
    """Cписок пользователей."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if (request and request.user.is_authenticated):
            return Follow.objects.filter(
                user=request.user,
                author=obj
            ).exists()
        return False


class UserCreateSerializer(serializers.ModelSerializer):
    """Создание нового пользователя."""

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password'
        )
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user


class SetPasswordSerializer(serializers.Serializer):
    """Изменение пароля пользователя."""

    current_password = serializers.CharField()
    new_password = serializers.CharField()

    def validate(self, obj):
        try:
            validate_password(obj['new_password'])
        except django_exceptions.ValidationError as e:
            raise serializers.ValidationError(
                {'new_password': list(e.messages)}
            ) from e
        return super().validate(obj)

    def update(self, instance, validated_data):
        if not instance.check_password(validated_data['current_password']):
            raise serializers.ValidationError(
                {'current_password': 'Неверный пароль'}
            )
        if (validated_data['current_password']
           == validated_data['new_password']):
            raise serializers.ValidationError(
                {'new_password': 'Новый пароль должен отличаться от текущего'}
            )
        instance.set_password(validated_data['new_password'])
        instance.save()
        return validated_data


class TagSerializer(serializers.ModelSerializer):
    """Серелизатор тэгов."""

    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug',
        )


# Ингредиенты
class IngredientSerializer(serializers.ModelSerializer):
    """Серелизатор ингредиентов."""

    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
        )
# =========================================================


class RecipeIngredientSerializer(serializers.ModelSerializer):
    # id = serializers.IntegerField(source='ingredient.id')
    # name = serializers.CharField(source='ingredient.name')
    # measurement_unit = serializers.CharField(
    #     source='ingredient.measurement_unit'
    # )

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount'
        )


# class IngredientAmountSerializer(serializers.ModelSerializer):
#     id = serializers.IntegerField()

#     class Meta:
#         model = IngredientSum
#         fields = ('id', 'amount')


#  Рецепты.
class RecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=False, allow_null=True)
    author = UserSerializer(read_only=True)
    tags = TagSerializer(read_only=True, many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    ingredients = RecipeIngredientSerializer(read_only=True, many=True)

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
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return request.user.favorites.filter(recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return request.user.shopping_cart.filter(recipe=obj).exists()


class RecipeCreateSerializer(RecipeSerializer):
    ingredients = RecipeIngredientSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )

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

    def taking_validated_data(self, validated_data):
        queryset_tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        queryset_amount_ingredients = []
        for new_ingredient in ingredients:
            ingredient = get_object_or_404(
                Ingredient,
                pk=new_ingredient['id']
            )
            amount_ingredient, created = (
                RecipeIngredient.objects.get_or_create(
                    ingredient=ingredient,
                    amount=new_ingredient['amount']
                )
            )
            if created:
                amount_ingredient.save()
            queryset_amount_ingredients.append(amount_ingredient)
        return queryset_tags, queryset_amount_ingredients

    def create(self, validated_data):
        author = self.context['request'].user
        queryset_tags, queryset_amount_ingredients = (
            self.taking_validated_data(validated_data)
        )
        recipe = Recipe.objects.create(
            **validated_data,
            author=author
        )
        recipe.tags.set(queryset_tags)
        recipe.ingredients.set(queryset_amount_ingredients)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        Recipe.objects.filter(recipe=instance).delete()
        super().update(instance, validated_data)
        Recipe.objects.bulk_create(
            [Recipe(
                ingredient=get_object_or_404(
                    Ingredient,
                    id=ingredient['ingredient']['id']
                    ),
                recipe=instance,
                amount=ingredient['amount']
            ) for ingredient in ingredients]
        )
        return instance


class RecipeShortSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=False, allow_null=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time'
        )


class FollowSerializer(UserSerializer):
    """Серелизатор подписок."""
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

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

    def get_recipes(self, obj):
        recipes_limit = (
            self.context['request'].query_params.get('recipes_limit')
        )
        recipes = obj.recipes.all()
        if recipes_limit is not None:
            recipes_limit = int(recipes_limit)
            serializer = RecipeShortSerializer(
                recipes[:recipes_limit], many=True
            )
        else:
            serializer = RecipeShortSerializer(recipes, many=True)
        return serializer.data

    def get_recipes_count(self, obj):
        return obj.recipes.count()
