# Generated by Django 4.0.4 on 2022-04-15 14:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('faucet', '0002_brightuser__verification_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='brightuser',
            name='address',
            field=models.CharField(default='', max_length=45),
            preserve_default=False,
        ),
    ]
