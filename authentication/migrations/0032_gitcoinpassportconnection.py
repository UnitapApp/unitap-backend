# Generated by Django 4.0.4 on 2024-03-31 13:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0031_userprofile_is_verified'),
    ]

    operations = [
        migrations.CreateModel(
            name='GitcoinPassportConnection',
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