# Generated by Django 4.0.4 on 2023-09-13 18:07

import core.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('prizetap', '0023_alter_constraint_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='raffle',
            name='prize_amount',
            field=core.models.BigNumField(max_length=200),
        ),
    ]
