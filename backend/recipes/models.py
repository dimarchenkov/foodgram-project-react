from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        verbose_name='Название тега',
        max_length=50,
        unique=True,
    )
    color = models.CharField(
        verbose_name='Цветовой HEX-код тега',
        max_length=100,
        unique=True,
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Слаг тега',
    )

    class Meta:
        verbose_name = 'Тег'

    def __str__(self):
        return str(self.name)


class Ingredient(models.Model):
    name = models.CharField(
        verbose_name='Название ингредиента',
        max_length=200,
    )
    measurement_unit = models.CharField(
        verbose_name='Единицы измерения ингредиента',
        max_length=200,
    )

    class Meta:
        verbose_name = "Ингредиент"
        ordering = ['name']

    def __str__(self):
        return str(self.name)


class IngredientSum(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='Название ингредиента',
        on_delete=models.CASCADE
    )
    amount = models.PositiveIntegerField(
        verbose_name='Количество ингредиента'
    )

    class Meta:
        verbose_name = "Ингредиент в рецептах с количеством"
        verbose_name_plural = "Ингредиенты в рецептах с количеством"
        ordering = ['ingredient']
        constraints = [
            models.UniqueConstraint(
                fields=['ingredient', 'amount'],
                name='unique_amountingredient_model'
            )
        ]

    def __str__(self):
        return self.ingredient.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        verbose_name='Автор рецепта',
        on_delete=models.CASCADE,
        related_name='recipes',
    )
    name = models.CharField(
        verbose_name='Название рецепта',
        max_length=200
    )
    image = models.ImageField(
        verbose_name='Картинка рецепта',
        upload_to='recipes/',
        help_text='Загрузите сюда картинку вашего рецепта'
    )
    text = models.TextField(
        verbose_name='Текст рецепта',
        help_text='Текстовое описание рецепта'
    )
    ingredients = models.ManyToManyField(
        IngredientSum,
        related_name='recipes',
        verbose_name='Ингредиенты рецепта'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Тэги рецепта'
    )
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления рецепта'
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата создания',
        auto_now_add=True
    )

    class Meta:
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ['-pub_date']

    def __str__(self):
        return str(self.name)


class FavoriteRecipe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite_recipes',
        verbose_name='Повар'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite_recipes',
        verbose_name='Избранный рецепт'
    )

    class Meta:
        verbose_name = "Избранный рецепт"
        ordering = ['user']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite_model'
            )
        ]

    def __str__(self):
        return self.user.username


class ShoppingList(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_list_recipes',
        verbose_name='Покупатель'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_list_recipes',
        verbose_name='Рецепт для покупки'
    )

    class Meta:
        verbose_name = "Список покупок"
        ordering = ['user']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopping_list_model'
            )
        ]

    def __str__(self):
        return self.user.username
