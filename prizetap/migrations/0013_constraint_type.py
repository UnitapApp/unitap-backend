# Generated by Django 4.0.4 on 2023-07-19 15:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('prizetap', '0012_raffleentry_multiplier'),
    ]

    operations = [
        migrations.AddField(
            model_name='constraint',
            name='type',
            field=models.CharField(choices=[('VER', 'Verification'), ('TIME', 'Time')], default='VER', max_length=10),
        ),
    ]
