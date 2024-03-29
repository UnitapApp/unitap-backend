# Generated by Django 4.0.4 on 2023-04-29 12:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('faucet', '0041_chain_enough_fee_multiplier'),
    ]

    operations = [
        migrations.CreateModel(
            name='LightningConfig',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('period', models.IntegerField(default=64800)),
                ('period_max_cap', models.BigIntegerField()),
                ('claimed_amount', models.BigIntegerField(default=0)),
                ('current_round', models.IntegerField(null=True)),
            ],
        ),
    ]
