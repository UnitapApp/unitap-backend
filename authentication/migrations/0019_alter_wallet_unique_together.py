# Generated by Django 4.0.4 on 2023-09-28 03:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0018_alter_wallet_unique_together_wallet_primary'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='wallet',
            unique_together=set(),
        ),
    ]
