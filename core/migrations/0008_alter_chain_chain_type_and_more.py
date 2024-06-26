# Generated by Django 4.0.4 on 2024-05-31 11:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_alter_chain_chain_type_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chain',
            name='chain_type',
            field=models.CharField(choices=[('EVM', 'EVM'), ('Solana', 'Solana'), ('Lightning', 'Lightning'), ('NONEVM', 'NONEVM'), ('NONEVMXDC', 'NONEVMXDC')], default='EVM', max_length=10),
        ),
        migrations.AlterField(
            model_name='walletaccount',
            name='network_type',
            field=models.CharField(choices=[('EVM', 'EVM'), ('Solana', 'Solana'), ('Lightning', 'Lightning'), ('NONEVM', 'NONEVM'), ('NONEVMXDC', 'NONEVMXDC')], default='EVM', max_length=10),
        ),
    ]
