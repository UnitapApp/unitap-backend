# Generated by Django 4.0.4 on 2024-02-14 09:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tokenTap', '0034_tokendistribution_distribution_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='tokendistribution',
            name='tx_hash',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
