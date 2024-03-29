# Generated by Django 4.0.4 on 2023-06-24 19:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('faucet', '0048_globalsettings_prizetap_weekly_claim_limit_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='claimreceipt',
            name='_status',
            field=models.CharField(choices=[('Pending', 'Pending'), ('Verified', 'Verified'), ('Rejected', 'Rejected'), ('Processed', 'Processed')], default='Pending', max_length=10),
        ),
        migrations.AlterField(
            model_name='transactionbatch',
            name='_status',
            field=models.CharField(choices=[('Pending', 'Pending'), ('Verified', 'Verified'), ('Rejected', 'Rejected'), ('Processed', 'Processed')], default='Pending', max_length=10),
        ),
    ]
