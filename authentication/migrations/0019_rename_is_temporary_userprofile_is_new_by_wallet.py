# Generated by Django 4.0.4 on 2023-10-10 17:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0018_userprofile_is_temporary'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userprofile',
            old_name='is_temporary',
            new_name='is_new_by_wallet',
        ),
    ]
