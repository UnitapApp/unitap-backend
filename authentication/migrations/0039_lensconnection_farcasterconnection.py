# Generated by Django 4.0.4 on 2024-07-10 14:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0038_userprofile_prizetap_winning_chance_number_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='LensConnection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('user_wallet_address', models.CharField(max_length=255)),
                ('user_profile', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='%(class)s', to='authentication.userprofile')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='FarcasterConnection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('user_wallet_address', models.CharField(max_length=255)),
                ('user_profile', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='%(class)s', to='authentication.userprofile')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
