# Generated by Django 4.0.4 on 2023-02-27 20:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0003_profile_user_solanawallet_evmwallet_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='initial_context_id',
            field=models.CharField(max_length=512, unique=True),
        ),
    ]
