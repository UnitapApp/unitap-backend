# Generated by Django 4.0.4 on 2022-12-05 06:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('faucet', '0029_chain_chain_type_chain_is_testnet'),
    ]

    operations = [
        migrations.AddField(
            model_name='chain',
            name='gas_image_url',
            field=models.URLField(blank=True, max_length=255, null=True),
        ),
    ]
