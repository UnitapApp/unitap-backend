# Generated by Django 4.0.4 on 2023-11-30 15:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0022_remove_wallet_primary'),
    ]

    operations = [
        migrations.AddField(
            model_name='wallet',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
