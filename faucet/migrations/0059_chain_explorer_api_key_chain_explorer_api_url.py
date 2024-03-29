# Generated by Django 4.0.4 on 2023-10-08 19:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('faucet', '0058_alter_claimreceipt_amount'),
    ]

    operations = [
        migrations.AddField(
            model_name='chain',
            name='explorer_api_key',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='chain',
            name='explorer_api_url',
            field=models.URLField(blank=True, max_length=255, null=True),
        ),
    ]
