# Generated by Django 4.0.4 on 2023-04-03 18:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('faucet', '0038_alter_claimreceipt__status_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chain',
            name='chain_type',
            field=models.CharField(choices=[('EVM', 'EVM'), ('Solana', 'Solana'), ('Lightning', 'Lightning'), ('NONEVM', 'NONEVM')], default='EVM', max_length=10),
        ),
    ]
