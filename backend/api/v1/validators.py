from django.core.exceptions import ValidationError


def validate_ingredients(data):
    if not data:
        raise ValidationError('Нет ингридиентов')

    valid_ingredients = {}

    for ingredient in data:
        valid_ingredients[ingredient['id']] = int(ingredient['amount'])

        if valid_ingredients[ingredient['id']] <= 0:
            raise ValidationError('Количество < 1.')

    return data


def validate_tags(data):
    if not data:
        raise ValidationError('Не указаны тэги.')
    return data
