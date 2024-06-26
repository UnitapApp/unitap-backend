# Generated by Django 4.0.4 on 2024-04-15 18:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_sponsor'),
        ('quiztap', '0009_competition_amount_won_competition_winner_count'),
    ]

    operations = [
        migrations.AlterField(
            model_name='competition',
            name='sponsor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='competitions', to='core.sponsor'),
        ),
    ]
