# Generated by Django 4.0.4 on 2024-01-09 08:20

from django.db import migrations, models
import django.db.models.expressions
import django.db.models.functions.text


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0027_alter_wallet_address_wallet_unique_wallet_address_and_more'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='wallet',
            name='unique_wallet_address',
        ),
        migrations.RemoveConstraint(
            model_name='wallet',
            name='unique_wallet_user_profile_address',
        ),
        migrations.AddConstraint(
            model_name='wallet',
            constraint=models.UniqueConstraint(django.db.models.functions.text.Lower('address'), django.db.models.expressions.F('wallet_type'), condition=models.Q(('deleted__isnull', True)), name='unique_wallet_address'),
        ),
        migrations.AddConstraint(
            model_name='wallet',
            constraint=models.UniqueConstraint(django.db.models.functions.text.Lower('address'), django.db.models.expressions.F('user_profile'), django.db.models.expressions.F('wallet_type'), name='unique_wallet_user_profile_address'),
        ),
    ]
