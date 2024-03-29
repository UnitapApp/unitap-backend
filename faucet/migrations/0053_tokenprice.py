# Generated by Django 4.0.4 on 2023-08-08 08:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('faucet', '0052_alter_claimreceipt__status_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='TokenPrice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('usd_price', models.CharField(max_length=255)),
                ('datetime', models.DateTimeField(auto_now_add=True)),
                ('last_updated', models.DateTimeField(auto_now=True, null=True)),
                ('price_url', models.URLField(blank=True, max_length=255)),
                ('symbol', models.CharField(max_length=255)),
            ],
        ),
    ]
