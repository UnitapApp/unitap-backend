# Generated by Django 5.0 on 2024-08-26 11:54

import cloudflare_images.field
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tokenTap', '0062_remove_tokendistribution_image_url_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tokendistribution',
            name='token_image_url',
            field=cloudflare_images.field.CloudflareImagesField(blank=True, upload_to='', variant='public'),
        ),
        migrations.AlterField(
            model_name='tokendistribution',
            name='image',
            field=cloudflare_images.field.CloudflareImagesField(blank=True, upload_to='', variant='public'),
        ),
    ]