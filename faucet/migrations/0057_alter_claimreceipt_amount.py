# Generated by Django 4.0.4 on 2023-10-02 21:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('faucet', '0056_alter_claimreceipt_amount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='claimreceipt',
            name='amount',
            field=models.BigIntegerField(),
        ),
    ]
