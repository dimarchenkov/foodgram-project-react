# Generated by Django 4.2.7 on 2023-11-29 13:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0001_initial'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='recipeingredient',
            name='unique_ingredient_recipe',
        ),
    ]