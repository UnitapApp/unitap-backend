# Generated by Django 4.0.4 on 2023-09-05 07:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('prizetap', '0019_alter_raffle_chain'),
    ]

    operations = [
        migrations.AlterField(
            model_name='raffle',
            name='deadline',
            field=models.DateTimeField(blank=True),
        ),
        migrations.AlterField(
            model_name='raffle',
            name='max_number_of_entries',
            field=models.IntegerField(blank=True),
        ),
    ]
