# Generated by Django 4.0.4 on 2024-06-28 15:51

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0037_alter_wallet_wallet_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='prizetap_winning_chance_number',
            field=models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)]),
        ),
        migrations.AlterField(
            model_name='wallet',
            name='address',
            field=models.CharField(db_index=True, max_length=512),
        ),
    ]
