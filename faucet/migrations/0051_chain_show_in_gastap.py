# Generated by Django 4.0.4 on 2023-07-11 08:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('faucet', '0050_alter_chain_max_claim_amount'),
    ]

    operations = [
        migrations.AddField(
            model_name='chain',
            name='show_in_gastap',
            field=models.BooleanField(default=True),
        ),
    ]
