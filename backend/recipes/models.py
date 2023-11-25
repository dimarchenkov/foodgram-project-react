"""Модели рецептов."""

from django.contrib.auth import get_user_model
from django.db import models
from django.core.validators import MinValueValidator

CustomUser = get_user_model()


class Ingredient(models.Model):
    """
     Представляет модель ингредиентов, используемую в рецептах.

     Атрибуты:
         name (str): Название ингредиента.
         Measure_unit (str): единица измерения ингредиента.

     Мета:
         verbose_name (str): удобочитаемое имя модели.
         порядок (список): порядок модели по умолчанию.

     Методы:
         __str__(): возвращает название ингредиента в виде строки.
    """
    name = models.CharField(
        max_length=200,
        verbose_name='Наименование'
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Единица измерения'
    )

    class Meta:
        """Класс Meta для модели Ingredient."""
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Tag(models.Model):
    """
        Представляет модель тегов, используемую для категоризации рецептов.

        Атрибуты:
            name (str): Имя тега.
            color (str): шестнадцатеричный код цвета тега.
            slug (str): пул тега.

        Мета:
            verbose_name (str): удобочитаемое имя модели.
            ограничения (список): ограничения модели.

        Методы:
            __str__(): возвращает имя тега в виде строки.
    """
    name = models.CharField(
        max_length=200,
        verbose_name='Наименование тэга'
    )
    color = models.CharField(
        max_length=7,
        verbose_name='Цвет'
    )
    slug = models.SlugField(max_length=200)

    class Meta:
        """Класс Meta для модели Tag."""
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'color', 'slug'],
                name='unique_name_color_slug'
            )
        ]

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """
    Представляет рецепт.

    Атрибуты:
        name (str): Название рецепта.
        tags (Tag): теги, связанные с рецептом.
        author (Пользователь): Автор рецепта.
        text (str): Текстовое описание рецепта.
        ingredients (Ingredient): Ингредиенты, использованные в рецепте.
        image (ImageField): изображение рецепта.
        cooking_time (int): время приготовления по рецепту.
        pub_date (DateTimeField): дата и время создания рецепта.

    Мета:
        verbose_name (str): удобочитаемое имя модели.
        порядок (список): порядок модели по умолчанию.

    Методы:
        __str__(): возвращает имя рецепта в виде строки.
    """
    name = models.CharField(
        max_length=200,
        verbose_name='Наименование'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Тэги'
    )
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта'
    )
    text = models.TextField(verbose_name='Текст')
    ingredients = models.ManyToManyField(
        Ingredient,
        through='recipeingredient',
        related_name='recipes',
        verbose_name='Ингредиент'
    )

    image = models.ImageField(
        upload_to='recipes/',
        verbose_name='Изображение',
    )
    cooking_time = models.PositiveIntegerField()
    pub_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Метакласс модели рецепта."""
        ordering = ('pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        """Возвращает название рецепта."""
        return self.name


class RecipeIngredient(models.Model):
    """
    Представляет модель M2M для ингредиентов в рецепте в
    определенном количестве.

    Атрибуты:
        recipe (Recipe): Рецепт, к которому принадлежит ингредиент.
        ingredient (Ingredient): Ингредиент.
        amount (int): количество ингредиента в рецепте.

    Мета:
        verbose_name (str): удобочитаемое имя модели.
        порядок (список): порядок модели по умолчанию.
        ограничения (список): ограничения модели.

    Методы:
        __str__(): возвращает строковое представление
        ингредиента с его количеством.
    """
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
        related_name='ingredient'
    )
    amount = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Количество'
    )

    class Meta:
        """Класс Meta модели RecipeIngredient."""
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_ingredient_recipe'
            )
        ]
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецепта'

    def __str__(self):
        return f'{self.ingredient}, кол-во: {self.amount}'


class FavoriteRecipe(models.Model):
    """
    Представляет модель M2M избранных рецептов пользователя.

    Атрибуты:
        user (User): Пользователь, который добавил рецепт в избранное.
        recipe (Recipe): Любимый рецепт.

    Мета:
        verbose_name (str): удобочитаемое имя модели.
        ordering (list): порядок модели по умолчанию.
        constraints (list): ограничения модели.

    Методы:
        __str__(): возвращает имя пользователя в виде строки.
    """
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='favorite_recipes',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Избранный рецепт'
    )

    class Meta:
        """Класс Meta для модели FavoriteRecipe."""
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        ordering = ('user',)
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_user_recipe'
            )
        ]

    def __str__(self):
        return self.user.username


class ShoppingCart(models.Model):
    """
    Представляет модель списка покупок для пользователя.

    Атрибуты:
        user (Пользователь): Пользователь, которому принадлежит список покупок.
        рецепт (Рецепт): Рецепт, который нужно добавить в список покупок.

    Мета:
        verbose_name (str): удобочитаемое имя модели.
        ordering (list): порядок модели по умолчанию.
        constraints (list): ограничения модели.

    Методы:
        __str__(): возвращает имя пользователя в виде строки.
    """
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart_recipes',
        verbose_name='Рецепт'
    )

    class Meta:
        """Класс Meta для модели ShoppingCard."""
        ordering = ('user',)
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopping_card_model'
            )
        ]

    def __str__(self):
        return f'Список покупок {self.user.username}'
